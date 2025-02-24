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
from llm import (
    get_response_from_llm,
    get_batch_responses_from_llm,
    extract_json_between_markers,
)

it_reviewer_system_prompt = (
    "You are an AI reviewer in the international trading company responsible for evaluating Letter of Credit (L/C) applications. "
    "Your mission is to assess if all contents described in L/C application are align with the contract. "
    "Be critical and cautious in your decision-making process. Your evaluations should be structured, concise, and accurate."
)

review_prompt= """
Follow these steps to evaluate the application:
Please carefully read through L/C application provided
For each content within L/C application, determine if the content is mentioned in the contract.
Please advice if any points in the L/C application is not mentioned in the contract or contradicts with the contract.
The context of L/C shall be included in the context of contract. It is okay to mention additional things in contract, but it is not allowed to mention additional things in L/C
Carefully review and advice any small mistakes in the L/C application.
Provide the results in a structured JSON format. 

Args: 
    description (str): A description of L/C application and corresponding contract

Returns:
    dict: A structured report any points in L/C that is not mentioned in the contract or contradicts with contract.

    output format should be as below:
    * Please only provide JSON output as string starting from { and ending with }

    {
        "comments": {
            "Decision": "Not Mentioned" or "Contradict" or "Mistake"
            "LC description": "The concerned sentence/paragraph mentioned in the L/C application",
            "Contract description": "The corresponding description in the contract. say 'Not mentioned', if not mentioned in the contract."
        }
        ...
    }

"""


def perform_review(
    application_text,
    contract_text,
    model,
    client,
    temperature=0.75,
    msg_history=None,
    return_msg_history=False,
):

    base_prompt = review_prompt
    base_prompt += f"L/C APPLICATION:\n{application_text}"
    base_prompt += f"CORRESPONDING CONTRACT:\n{contract_text}"

    llm_review, msg_history = get_response_from_llm(
        base_prompt,
        model=model,
        client=client,
        system_message=it_reviewer_system_prompt,
        print_debug=False,
        msg_history=msg_history,
        temperature=temperature,
    )

    # Extract JSON from response
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

    return review


# feedback_prompt= """
# Please provide constructive advice comment to applicants.
# For example, how the applicant can enhance their strengths and mitigate the risks given these information.
# Please provide brief feedback in less than 100 words.
# """

# def provide_feedback(
#     application_text,
#     review_text,
#     model,
#     client,
#     temperature=0.75,
#     msg_history=None,
#     return_msg_history=False,
# ):

#     base_prompt = feedback_prompt + "\nReview Result:\n" + review_text + "\nApplication Content:\n" + application_text

#     llm_review, msg_history = get_response_from_llm(
#         base_prompt,
#         model=model,
#         client=client,
#         system_message=it_reviewer_system_prompt,
#         print_debug=False,
#         msg_history=msg_history,
#         temperature=temperature,
#     )

#     return llm_review


def load_docs(path, num_pages=None, min_size=100):
    """
    Convert folder or file path to string content for input to LLM.
    Handles application and appendix cases differently.
    
    Args:
        path (str): The folder path containing files to be processed.
        num_pages (int, optional): Maximum number of pages to process. Defaults to None (process all pages).
        min_size (int, optional): Minimum size of text. Defaults to 100.

    Returns:
        str: Extracted text content.
    """
    try:
        # Find application file starting with 'app_'
        app_file = None
        appendix_folder = None

        for root, dirs, files in os.walk(path):
            for file in files:
                if file.startswith("app_") and file.endswith(".txt"):
                    app_file = os.path.join(root, file)
                    break

            if "Appendix" in dirs:
                appendix_folder = os.path.join(root, "Appendix")

            if app_file and appendix_folder:
                break

        if not app_file:
            raise FileNotFoundError("Application file starting with 'app_' not found.")

        if not appendix_folder:
            raise FileNotFoundError("Appendix folder not found.")

        # Process application file
        with open(app_file, "r") as f:
            application_text = f.read()

        # Process appendix folder
        appendix_text = "APPENDIX TO THIS APPLICATION:\n"
        for root, _, files in os.walk(appendix_folder):
            for file in files:
                if file.endswith(".pdf"):
                    pdf_path = os.path.join(root, file)
                    appendix_text += f"\n--- Start of {file} ---\n"
                    appendix_text += extract_pdf_text(pdf_path, num_pages)
                    appendix_text += f"\n--- End of {file} ---\n"

        # Combine texts
        combined_text = application_text + "\n" + appendix_text

        if len(combined_text) < min_size:
            raise Exception("Combined text too short")

        return combined_text

    except Exception as e:
        print(f"Error: {e}")
        return ""


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

        