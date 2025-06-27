from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file='.env', env_file_encoding='utf-8', extra='ignore')

    FIRESTORE_PROJECT_ID: str
    VERTEXAI_LOCATION: str
    VERTEXAI_MODEL_NAME: str
    FIRESTORE_DB: str

settings = Settings()