import os
from dotenv import load_dotenv
from typing import Optional

# Load the .env file
load_dotenv()

# Exact ordered column sequence matching your XGBoost model schema
MODEL_COLUMNS = [
    "discharge_year",
    "age_group18-29",
    "age_group30-49",
    "raceBlack/African American",
    "raceMulti-racial",
    "raceOther Race",
    "raceWhite",
    "ethnicityMulti-ethnic",
    "ethnicityNot Span/Hispanic",
    "ethnicitySpanish/Hispanic",
    "ethnicityUnknown",
    "length_of_stay",
    "apr_severity_of_illness_descriptionMajor",
    "apr_severity_of_illness_descriptionMinor",
    "apr_severity_of_illness_descriptionModerate",
    "payment_typology_1Blue Cross/Blue Shield",
    "payment_typology_1Private Health Insurance",
    "type_of_admissionElective",
    "type_of_admissionEmergency",
    "type_of_admissionUrgent",
    "hospital_countyBronx",
    "hospital_countyKings",
    "hospital_countyNew York",
    "hospital_countyQueens",
    "hospital_countyRichmond",
    "hospital_tierPublic",
    "hospital_tierCommunity",
    "hospital_tierPrivate System",
]

# Mapping structure linking base keys to valid model suffix names
CAT_MAPS = {
    "age_group": ["18-29", "30-49"],
    "race": ["Black/African American", "Multi-racial", "Other Race", "White"],
    "ethnicity": ["Multi-ethnic", "Not Span/Hispanic", "Spanish/Hispanic", "Unknown"],
    "apr_severity_of_illness_description": ["Major", "Minor", "Moderate"],
    "payment_typology_1": ["Blue Cross/Blue Shield", "Private Health Insurance"],
    "type_of_admission": ["Elective", "Emergency", "Urgent"],
    "hospital_county": ["Bronx", "Kings", "New York", "Queens", "Richmond"],
    "hospital_tier": ["Public", "Community", "Private System"],
}


AWS_REGION: Optional[str] = os.getenv("AWS_REGION")
LLM_TO_USE: Optional[str] = os.getenv("LLM_TO_USE")
ANTHROPIC_LLM_MODEL: Optional[str] = os.getenv("ANTHROPIC_LLM_MODEL")
OLLAMA_LLM_MODEL: Optional[str] = os.getenv("OLLAMA_LLM_MODEL")
HUGGING_FACE_LLM_MODEL: Optional[str] = os.getenv("HUGGING_FACE_LLM_MODEL")
HUGGING_FACE_TOKENIZER_MODEL: Optional[str] = os.getenv("HUGGING_FACE_TOKENIZER_MODEL")
HUGGING_FACE_CONTEXT_WINDOW: Optional[int] = int(
    os.getenv("HUGGING_FACE_CONTEXT_WINDOW", "16384")
)
HUGGING_FACE_TEMPERATURE: Optional[float] = float(
    os.getenv("HUGGING_FACE_TEMPERATURE", "0.7")
)
HUGGING_FACE_MAX_NEW_TOKENS: Optional[int] = int(
    os.getenv("HUGGING_FACE_MAX_NEW_TOKENS", "4096")
)
DEFAULT_NUM_OUTPUTS: Optional[int] = int(os.getenv("DEFAULT_NUM_OUTPUTS", "512"))
ANTHROPIC_MAX_TOKENS: Optional[int] = int(os.getenv("ANTHROPIC_MAX_TOKENS", "8192"))
OLLAMA_MAX_TOKENS: Optional[int] = int(os.getenv("OLLAMA_MAX_TOKENS", "8192"))
OLLAMA_REQUEST_TIMEOUT = os.getenv("OLLAMA_REQUEST_TIMEOUT")
DEFAULT_NUM_GPU: Optional[int] = int(os.getenv("DEFAULT_NUM_GPU", "-1"))
OLLAMA_MAX_MEMORY: Optional[int] = int(os.getenv("OLLAMA_MAX_MEMORY", "512"))
OLLAMA_DEFAULT_TIMEOUT: Optional[float] = float(os.getenv("OLLAMA_MAX_TOKENS", "120.0"))
BEDROCK_LLM_MODEL: Optional[str] = os.getenv("BEDROCK_LLM_MODEL")
BEDROCK_MAX_TOKENS: Optional[int] = int(os.getenv("BEDROCK_MAX_TOKENS", "8192"))
