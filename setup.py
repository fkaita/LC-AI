from setuptools import setup, find_packages

setup(
    name="LC-AI",  # Replace with your project name
    version="0.1.0",
    package_dir={"": "code"},  # Root of the packages is the "code" directory
    packages=find_packages(where="code"),  # Look for packages inside "code"
    install_requires=[
        "openai",
        "backoff",
        "anthropic",
        "python-dotenv",
        "pymupdf",
        "PyPDF2",
        "pandas",
        "tabulate"
    ],
    description="AI-powered Letter of Credit",
    author="Kaita Furukawa",
    url="https://github.com/fkaita/LC-AI",  # Optional, add your repository URL
)
