import os
from dotenv import load_dotenv
load_dotenv()  # Load variables from .env

from llm import create_client
from review import extract_pdf_text, perform_review
import pandas as pd

# Create a real client
api_key = os.getenv("OPENAI_API_KEY")
client, model = create_client("gpt-4o-2024-05-13")

app_paths = ["001"]
path = "docs/application/"
output_path = "docs/review/"

results = []
# feedback_results= []
for application in app_paths:
    print(f"Review for {application} was started...")
    # Output format
    result = {}

    # Load application and related document
    file_path = path + application
    application_text = extract_pdf_text(file_path + "/application.pdf")
    contract_text = extract_pdf_text(file_path + "/contract.pdf")

    # Call the function
    review = perform_review(
        application_text=application_text,
        contract_text=contract_text,
        model=model,
        client=client,
    )

    # Convert the dictionary to a string representation
    result["review_result"] = review
    table = pd.DataFrame.from_dict(review, orient='index')
    review_text = table.to_markdown()

    # # Call the function
    # feedback = provide_feedback(
    #     application_text=app_docs,
    #     review_text=review_text,
    #     model=model,
    #     client=client,
    # )
    # result["feedback_result"] = feedback

    output_file = f"{output_path}{application}.md"
    # os.makedirs(os.path.dirname(output_file), exist_ok=True)
    # Save as a properly formatted Markdown file
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(f"# Review Result for Application ID: {application}\n\n")
        
        f.write("## Review Result\n\n")
        f.write(table.to_markdown())
        f.write("```\n\n")

        # f.write("## Feedback\n\n")
        # f.write(feedback + "\n")

    print(f"Review for {application} was finished!")

# Print the result
print("Review was completed")
print(review_text)