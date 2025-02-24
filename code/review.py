"""
This script utilizes or is inspired by the code and concepts from the following GitHub repository:
Repository: AI-Scientist
URL: https://github.com/SakanaAI/AI-Scientist
Author: SakanaAI
"""


import os
import numpy as np
import re
import json
import re
from PyPDF2 import PdfReader
import fitz
from llm import get_response_from_llm


def extract_pdf_text(pdf_path, num_pages=None):
    """
    Extract text from a PDF file using PyMuPDF or PyPDF2.

    Args:
        pdf_path (str): Path to the PDF file.
        num_pages (int, optional): Maximum number of pages to process. Defaults to None (process all pages).

    Returns:
        str: Extracted text from the PDF file.
    """
    try:
        # Try using PyMuPDF
        doc = fitz.open(pdf_path)
        text = ""
        for i, page in enumerate(doc):
            if num_pages and i >= num_pages:
                break
            text += page.get_text()
        doc.close()
        return text
    except Exception as e:
        print(f"Error with PyMuPDF: {e}")

    try:
        # Fallback to PyPDF2
        reader = PdfReader(pdf_path)
        text = ""
        for i, page in enumerate(reader.pages):
            if num_pages and i >= num_pages:
                break
            text += page.extract_text()
        return text
    except Exception as e:
        print(f"Error with PyPDF2: {e}")

    return ""


async def review_lc(
    model,
    client,
    lc_filepath,
    contract_filepath
):
    
    it_reviewer_system_prompt = (
        "You are an AI reviewer in the international trading company responsible for evaluating Letter of Credit (L/C) applications. "
        "Your mission is to assess if all contents described in L/C application are align with the contract. "
        "Be critical and cautious in your decision-making process. Your evaluations should be structured, concise, and accurate."
    )

    # STEP 1: Split L/C
    base_prompt = """
    Please split following document into multiple parts by content.
    *Please just split the original text without changing any words even if original text contains typo or mistake.
    *Please split without overlapping
    *Please provide output in JSON.

    Args: 
        application text (str): A texts from document 

    Returns:
        dict: A list of splitted text.

        output format should be as below:
        * Please only provide JSON output as string starting from { and ending with }

        {
            "output": ["list of splitted texts", "list of splitted texts", "list of splitted texts"...]
            ...
        }

    """
    yield "progress-message: Analyzing L/C draft...\n"

    application_text = extract_pdf_text(lc_filepath)
    base_prompt += f"Document: {application_text}"

    llm_review, _ = get_response_from_llm(
        base_prompt,
        model=model,
        client=client,
        system_message=it_reviewer_system_prompt,
        print_debug=False,
    )

    try:
        json_match = re.search(r"{.*}", llm_review, re.DOTALL)
        if json_match:
            cleaned_review = json_match.group(0)
            review = json.loads(cleaned_review)
        else:
            raise ValueError("No JSON found in response")
    except json.JSONDecodeError as e:
        print(f"JSON decoding failed: {e}")
        print(f"LLM response: {llm_review}")
        review = None
        return 

    print("1/3 finished")

    # STEP 2: check discrepancy with contract
    yield "progress-message: Checking L/C draft with contract...\n"
    contract_text = extract_pdf_text(contract_filepath)
    result = ""
    for text in review["output"]:
        base_prompt = f"""
        Below paragraph is extracted from a L/C application. Please carefully read the content and advice if any discrepancy exists with given contract.
        Please only provide identified discrepancy in your response.
        If you do not find any discrepancy, just mention no discrepancy.

        EXTRACTED PARAGRAPH FROM L/C APPLICATION:
        {text}

        PROVIDED CONTRACT:
        {contract_text}
        """

        llm_review, _ = get_response_from_llm(
            base_prompt,
            model=model,
            client=client,
            system_message=it_reviewer_system_prompt,
            print_debug=False,
        )

        result += llm_review

    print("2/3 finished")

    # STEP 3: provide summary
    yield "progress-message: Making summary...\n"
    base_prompt = f"""
    Please summarize the discrepancy found in the the below report.

    Report:
    {result}
    """

    llm_review, _ = get_response_from_llm(
        base_prompt,
        model=model,
        client=client,
        system_message=it_reviewer_system_prompt,
        print_debug=False,
    )

    print("3/3 finished")
    yield "progress-message: Finished!\n"

    yield "final-message: " + llm_review

        