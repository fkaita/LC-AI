from setuptools import setup, find_packages

setup(
    name="project-name",  # Replace with your project name
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
    description="AI-powered Japanese Ringi system",
    author="Kaita Furukawa",
    url="https://github.com/fkaita/Ringi-AI",  # Optional, add your repository URL
)
