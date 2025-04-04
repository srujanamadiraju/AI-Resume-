'''
-----------------------------------------------------------------------
File: LLM.py
Creation Time: Nov 1st 2023 1:40 am
Author: Saurabh Zinjad
Developer Email: zinjadsaurabh1997@gmail.com
Copyright (c) 2023 Saurabh Zinjad. All rights reserved | GitHub: Ztrimus
-----------------------------------------------------------------------
'''
import json
import textwrap
import pandas as pd
import streamlit as st
from transformers import pipeline

from zlm.utils.utils import parse_json_markdown
from zlm.variables import DEEPSEEK_EMBEDDING_MODEL

class DeepSeekModel:
    def __init__(self, api_key, system_prompt):
        self.system_prompt = system_prompt
        self.client = pipeline("text-generation", model="deepseek-ai/DeepSeek-V3-0324", api_key=api_key, trust_remote_code=True)
    
    def get_response(self, prompt, expecting_longer_output=False, need_json_output=False):
        user_prompt = f"{self.system_prompt}\n{prompt}"
        chunk_size = 1024  # Define your chunk size
        responses = []

        try:
            for i in range(0, len(user_prompt), chunk_size):
                chunk = user_prompt[i:i + chunk_size]
                completion = self.client(chunk, max_length=4000 if expecting_longer_output else None, return_full_text=False)
                content = completion[0]['generated_text'].strip()
                responses.append(content)
            
            full_response = " ".join(responses)
            
            if need_json_output:
                return parse_json_markdown(full_response)
            else:
                return full_response
        
        except Exception as e:
            print(e)
            st.error(f"Error in Hugging Face API, {e}")
            st.markdown("<h3 style='text-align: center;'>Please try again! Check the log in the dropdown for more details.</h3>", unsafe_allow_html=True)
    
    def get_embedding(self, text, model=DEEPSEEK_EMBEDDING_MODEL, task_type="retrieval_document"):
        try:
            text = text.replace("\n", " ")
            return self.client.embeddings.create(input = [text], model=model).data[0].embedding
        except Exception as e:
            print(e)
