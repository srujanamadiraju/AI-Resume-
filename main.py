"""
-----------------------------------------------------------------------
File: main.py
Creation Time: Nov 24th 2023 7:04 pm
Author: Saurabh Zinjad
Developer Email: zinjadsaurabh1997@gmail.com
Copyright (c) 2023 Saurabh Zinjad. All rights reserved | GitHub: Ztrimus
-----------------------------------------------------------------------
"""

import argparse
from zlm import AutoApplyModel
import os
import json

def create_resume_cv(url, master_data_path, api_key, downloads_dir):
    """
    Creates a resume or CV using the Job-LLM model.

    Args:
        url (str): The URL of the job posting or description.
        master_data_path (str): The path to the master data file containing information about the candidate.
        api_key (str): The API key for Hugging Face.
        downloads_dir (str): The directory where the generated resume or CV will be saved.

    Returns:
        None
    """
    # Load master data from file
    with open(master_data_path, 'r') as file:
        master_data = json.load(file)

    # Initialize the model with Hugging Face's DeepSeek-V3-0324
    job_llm = AutoApplyModel(api_key, downloads_dir, "deepseek-ai/DeepSeek-V3-0324")

    # Send data in chunks
    chunk_size = 1024  # Define your chunk size
    for i in range(0, len(master_data), chunk_size):
        chunk = master_data[i:i + chunk_size]
        job_llm.resume_cv_pipeline(url, chunk)


if __name__ == "__main__":
    # Create an argument parser
    parser = argparse.ArgumentParser()

    # Add the required arguments
    parser.add_argument("-u", "--url", help="URL of the job posting")
    parser.add_argument("-m", "--master_data", help="Path of user's master data file.")
    parser.add_argument("-k", "--api_key", default="os", help="LLM Provider API Keys")
    parser.add_argument("-d", "--downloads_dir", help="Give detailed path of folder")

    # Parse the arguments
    args = parser.parse_args()

    create_resume_cv(
        args.url, args.master_data, args.api_key, args.downloads_dir
    )