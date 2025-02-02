from review import load_docs

def test_load_docs():
    """Test the load_docs function with a real folder structure."""
    # Path to the real directory and document
    real_path = "docs/application/24-001_backlog"

    try:
        # Run the function with the real directory
        result = load_docs(real_path)
        print("Test Result:")
        print(result)
    except Exception as e:
        print(f"Test failed: {e}")

# Execute the test
test_load_docs()
