from llm import create_client, get_response_from_llm

def main():
    import os
    from dotenv import load_dotenv
    load_dotenv()  # Load variables from .env
    api_key = os.getenv("OPENAI_API_KEY")

    # Set your OpenAI API key
    os.environ["OPENAI_API_KEY"] = api_key
    
    # Define model and test inputs
    model_name = "gpt-4o-2024-05-13"
    msg = "What is the capital of France?"
    system_message = "You are a helpful assistant."
    msg_history = [{"role": "user", "content": "Hello!"}]
    
    # Create the client
    client, model = create_client(model_name)
    
    # Call the function
    try:
        response, updated_history = get_response_from_llm(
            msg=msg,
            client=client,
            model=model,
            system_message=system_message,
            msg_history=msg_history,
            temperature=0.7,
        )
        print("Response from model:")
        print(response)
    except Exception as e:
        print("Error occurred:", e)

if __name__ == "__main__":
    main()
