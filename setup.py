from setuptools import setup, find_packages

setup(
    name="ai-resume-builder",
    version="0.1",
    packages=find_packages(),
    install_requires=[
        "fastapi",
        "uvicorn",
        "python-multipart",
        "pillow",
        "nltk",
        "python-dotenv",
    ],
) 