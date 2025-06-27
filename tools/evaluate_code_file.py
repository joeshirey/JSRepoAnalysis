from .base_tool import BaseTool
import os
import json
import vertexai
from vertexai.generative_models import GenerativeModel, Part, GenerationConfig
from utils.logger import logger
from utils.exceptions import CodeEvaluatorError

class CodeEvaluator(BaseTool):
    def __init__(self, config):
        self.config = config
        try:
            vertexai.init(project=self.config.FIRESTORE_PROJECT_ID, location=self.config.VERTEXAI_LOCATION)
            self.model = GenerativeModel(self.config.VERTEXAI_MODEL_NAME)
        except Exception as e:
            raise CodeEvaluatorError(f"Error initializing Vertex AI: {e}")

    def execute(self, file_path, language, region_tag):
        """
        Evaluates code using the Gemini 2.5 Flash model on Vertex AI.
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                code = file.read()
        except FileNotFoundError:
            raise CodeEvaluatorError(f"File not found at path: {file_path}")
        except Exception as e:
            raise CodeEvaluatorError(f"Error reading file: {e}")

        # Read prompt from file
        try:
            with open("./prompts/consolidated_eval.txt", "r") as f:
                prompt_template = f.read()
        except FileNotFoundError:
            raise CodeEvaluatorError("Prompt file not found.")
        except Exception as e:
            raise CodeEvaluatorError(f"Error reading prompt file: {e}")

        # Inject code into prompt
        prompt = self._fill_prompt_placeholders(prompt_template_string=prompt_template, language=language, code_sample=code, github_link=file_path, region_tag=region_tag)

        # Configure generation parameters
        generation_config = GenerationConfig(
            temperature=0.1,
            top_p=0.9,
        )

        try:
            response = self.model.generate_content(
                prompt,
                generation_config=generation_config
            )
            return response.candidates[0].content.parts[0].text
        except Exception as e:
            raise CodeEvaluatorError(f"Error generating content from Vertex AI: {e}")

    def _fill_prompt_placeholders(self, prompt_template_string: str, language: str, code_sample: str, github_link: str, region_tag: str) -> str:
        """
        Replaces placeholders in an existing prompt template string.
        """
        language_lowercase = language.lower()
        filled_prompt = prompt_template_string.replace("{{LANGUAGE}}", language)
        filled_prompt = filled_prompt.replace("{{LANGUAGE_LOWERCASE}}", language_lowercase)
        filled_prompt = filled_prompt.replace("{{CODE_SAMPLE}}", code_sample)
        filled_prompt = filled_prompt.replace("{{uri_placeholder}}", github_link)
        filled_prompt = filled_prompt.replace("{{region_tag_id_placeholder}}", region_tag)
        return filled_prompt
