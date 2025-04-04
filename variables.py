'''
-----------------------------------------------------------------------
File: zlm/variables.py
Creation Time: Aug 18th 2024, 5:26 am
Author: Saurabh Zinjad
Developer Email: saurabhzinjad@gmail.com
Copyright (c) 2023-2024 Saurabh Zinjad. All rights reserved | https://github.com/Ztrimus
-----------------------------------------------------------------------
'''

from zlm.prompts.sections_prompt import EXPERIENCE, SKILLS, PROJECTS, EDUCATIONS, CERTIFICATIONS, ACHIEVEMENTS
from zlm.schemas.sections_schemas import Achievements, Certifications, Educations, Experiences, Projects, SkillSections
from zlm.utils.utils import key_value_chunking  # Assuming this function is used for chunking

# Updated to use Hugging Face's DeepSeek model
DEEPSEEK_EMBEDDING_MODEL = "deepseek-ai/DeepSeek-V3-0324"

DEFAULT_LLM_PROVIDER = "HuggingFace"
DEFAULT_LLM_MODEL = DEEPSEEK_EMBEDDING_MODEL

LLM_MAPPING = {
    'HuggingFace': {
        "api_env": "HUGGINGFACE_API_KEY",
        "model": [DEEPSEEK_EMBEDDING_MODEL],
        "trust_remote_code": True,  # Added to allow custom code execution
    }
}

section_mapping = {
    "work_experience": {"prompt": EXPERIENCE, "schema": Experiences},
    "skill_section": {"prompt": SKILLS, "schema": SkillSections},
    "projects": {"prompt": PROJECTS, "schema": Projects},
    "education": {"prompt": EDUCATIONS, "schema": Educations},
    "certifications": {"prompt": CERTIFICATIONS, "schema": Certifications},
    "achievements": {"prompt": ACHIEVEMENTS, "schema": Achievements},
}

def send_data_in_chunks(data, chunk_size=1000):
    """Send data in chunks to the API."""
    chunks = key_value_chunking(data, chunk_size)
    for chunk in chunks:
        # Here you would send each chunk to the API
        # Example: api.send(chunk)
        pass