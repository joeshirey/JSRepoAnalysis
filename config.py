import os
from dotenv import load_dotenv

class Config:
    """
    A central configuration object for the application.
    """

    def __init__(self):
        load_dotenv(override=True)
        self.project_id = os.getenv("FIRESTORE_PROJECT_ID")
        self.vertexai_location = os.getenv("VERTEXAI_LOCATION")
        self.vertexai_model_name = os.getenv("VERTEXAI_MODEL_NAME")
        self.firestore_db = os.getenv("FIRESTORE_DB")

        if not all([self.project_id, self.vertexai_location, self.vertexai_model_name, self.firestore_db]):
            raise ValueError("One or more required environment variables are not set.")
