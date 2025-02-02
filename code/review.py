"""
This script utilizes or is inspired by the code and concepts from the following GitHub repository:
Repository: AI-Scientist
URL: https://github.com/SakanaAI/AI-Scientist
Author: SakanaAI
"""


import os
import numpy as np
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
    "You are an AI reviewer in the IT department responsible for evaluating internal applications from employees. "
    "Your mission is to assess risks and merits related to IT tools and the infrastructure of the company. "
    "Be critical and cautious in your decision-making process. Your evaluations should be structured, concise, and actionable."
)

review_prompt= """
Follow these steps to evaluate the application:
Please carefully read through review criteria provided by the department
For each criterion, determine if it is Pass or Reject based on the provided details.
For each criterion, provide reason for the decision.
Provide the results in a structured JSON format.

Args: 
    application_description (str): A description of the application with appendix documents

Returns:
    dict: A structured report containing Pass or Reject decision of each criteria with reasons.

    output format should be as below:
    * Please remain original criteria ID and criteria name as key, "CriteriaID_CriteriaName" 
    * Please only provide JSON output as string starting from { and ending with }

    {
        "CriteriaID_CriteriaName": {
            "Decision": "Pass" or "Reject",
            "Reason": "Clear explanation of the reason for the decision"
        }
        ...
    }

"""


def perform_review(
    text,
    model,
    client,
    temperature=0.75,
    msg_history=None,
    return_msg_history=False,
):

    base_prompt = review_prompt

    rc_prompt = "REVIEW CRITERIA OF IT DEPARTMENT:\n"

    dir_path = os.path.dirname(os.path.realpath(__file__))
    file_path = os.path.join(dir_path, "review_criteria/it_review_criteria")
    if not os.path.exists(file_path):
        print(f"The file at {file_path} does not exist.")
    else:
        try:
            with open(file_path, "r", encoding="utf-8") as file:
                rc_prompt = file.read()
        except IOError as e:
            print(f"An error occurred while reading the file: {e}")

    base_prompt += rc_prompt

    base_prompt += f"""
    Here is the application you are asked to review:
    ```
    {text}
    ```"""

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



feedback_prompt= """
Please provide constructive advice comment to applicants.
For example, how the applicant can enhance their strengths and mitigate the risks given these information.
Please provide brief feedback in less than 100 words.
"""

def provide_feedback(
    application_text,
    review_text,
    model,
    client,
    temperature=0.75,
    msg_history=None,
    return_msg_history=False,
):

    base_prompt = feedback_prompt + "\nReview Result:\n" + review_text + "\nApplication Content:\n" + application_text

    llm_review, msg_history = get_response_from_llm(
        base_prompt,
        model=model,
        client=client,
        system_message=it_reviewer_system_prompt,
        print_debug=False,
        msg_history=msg_history,
        temperature=temperature,
    )

    return llm_review


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