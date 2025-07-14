from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file='.env', env_file_encoding='utf-8', extra='ignore')

    GOOGLE_CLOUD_PROJECT: str
    GOOGLE_CLOUD_LOCATION: str
    VERTEXAI_MODEL_NAME: str
    FIRESTORE_DB: str
    BIGQUERY_DATASET: str
    BIGQUERY_TABLE: str
    GOOGLE_GENAI_USE_VERTEXAI: bool = True

settings = Settings()