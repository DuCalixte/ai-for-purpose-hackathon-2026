from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    # Uploading system data
    APP_OID: str = "nyc_hospital_sparcs_agent"
    APP_NAME: str = "NYC Hospital SPARCS Agent"
    ENVIRONMENT: str = "development"
    API_V1_STR: str = "/api/v1"
    APP_STATUS: str = "/api/app_status"
