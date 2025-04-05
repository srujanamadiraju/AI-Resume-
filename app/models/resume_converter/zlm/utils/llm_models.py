
import json
import textwrap
import pandas as pd
import streamlit as st
from openai import OpenAI
from langchain_community.llms.ollama import Ollama
from langchain_ollama import OllamaEmbeddings
import google.generativeai as genai
from google.generativeai.types.generation_types import GenerationConfig

from models.resume_converter.zlm.utils.utils import parse_json_markdown
from models.resume_converter.zlm.variables import GPT_EMBEDDING_MODEL
from litellm import completion, embedding
from models.resume_converter.zlm.utils.utils import parse_json_markdown

class PerplexityLiteLLM:
    def __init__(self, api_key, model, system_prompt):
        self.api_key = api_key
        self.model = model
        self.system_prompt = system_prompt

    def get_response(self, prompt, expecting_longer_output=False, need_json_output=False):
        try:
            messages = [{"role": "system", "content": self.system_prompt}] if self.system_prompt.strip() else []
            messages.append({"role": "user", "content": prompt})

            response = completion(
                model=self.model,
                messages=messages,
                api_key=self.api_key,
                temperature=0.7,
                max_tokens=4000 if expecting_longer_output else 2048,
                base_url="https://api.perplexity.ai"
            )

            content = response.choices[0].message["content"].strip()
            return parse_json_markdown(content) if need_json_output else content

        except Exception as e:
            print(f"[LiteLLM Error] {e}")
            return None

    def get_embedding(self, text, model="text-embedding-3-small", task_type="retrieval_document"):
        try:
            response = embedding(
                model=model,
                input=text,
                api_key=self.api_key,
                base_url="https://api.perplexity.ai"
            )
            return response["data"][0]["embedding"]
        except Exception as e:
            print(f"[LiteLLM Embedding Error] {e}")
            return None
