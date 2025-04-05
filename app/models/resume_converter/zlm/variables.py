
from models.resume_converter.zlm.prompts.sections_prompt import EXPERIENCE, SKILLS, PROJECTS, EDUCATIONS, CERTIFICATIONS, ACHIEVEMENTS
from models.resume_converter.zlm.schemas.sections_schemas import Achievements, Certifications, Educations, Experiences, Projects, SkillSections

GPT_EMBEDDING_MODEL = "text-embedding-3-small"

DEFAULT_LLM_PROVIDER = "Perplexity"
DEFAULT_LLM_MODEL = "mistral-7b-instruct"

LLM_MAPPING = {
    'Perplexity': {
        "api_env": "PERPLEXITY_API_KEY",
        "model": ["sonar-pro", "sonar-reasoning-pro", "sonar-reasoning", "sonar"],
    }
}


section_mapping = {
    "work_experience": {"prompt":EXPERIENCE, "schema": Experiences},
    "skill_section": {"prompt":SKILLS, "schema": SkillSections},
    "projects": {"prompt":PROJECTS, "schema": Projects},
    "education": {"prompt":EDUCATIONS, "schema": Educations},
    "certifications": {"prompt":CERTIFICATIONS, "schema": Certifications},
    "achievements": {"prompt":ACHIEVEMENTS, "schema": Achievements},
}