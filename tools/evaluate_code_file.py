from .base_tool import BaseTool
import os
import json
import vertexai
from vertexai.generative_models import GenerativeModel, Part, GenerationConfig

class CodeEvaluator(BaseTool):
    def execute(self, file_path, language):
        """
        Evaluates code using the Gemini 2.5 Flash model on Vertex AI.
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                code = file.read()
        except FileNotFoundError:
            return json.dumps({"error": f"File not found at path: {file_path}"})
        except Exception as e:
            return json.dumps({"error": f"Error reading file: {e}"})

        # Read prompt from file
        try:
            with open("./prompts/consolidated_eval.txt", "r") as f:
                prompt_template = f.read()
        except FileNotFoundError:
            return json.dumps({"error": "Prompt file not found."})
        except Exception as e:
            return json.dumps({"error": f"Error reading prompt file: {e}"})

        # Inject code into prompt
        prompt = self._fill_prompt_placeholders(prompt_template_string=prompt_template, language=language, code_sample=code)

        # Vertex AI configuration
        PROJECT_ID = os.getenv("PROJECT_ID")
        LOCATION = os.getenv("VERTEXAI_LOCATION")
        MODEL_NAME = os.getenv("VERTEXAI_MODEL_NAME")

        if not PROJECT_ID or not LOCATION or not MODEL_NAME:
            return json.dumps({"error": "Missing Vertex AI environment variables (PROJECT_ID, VERTEXAI_LOCATION, or VERTEXAI_MODEL_NAME)."})

        # Initialize Vertex AI client
        try:
            vertexai.init(project=PROJECT_ID, location=LOCATION)
            model = GenerativeModel(MODEL_NAME)
        except Exception as e:
            return json.dumps({"error": f"Error initializing Vertex AI client or model: {e}"})

        # Configure generation parameters
        generation_config = GenerationConfig(
            temperature=0.1,
            top_p=0.9,
        )

        response = model.generate_content(
            prompt,
            generation_config=generation_config
        )

        return response.candidates[0].content.parts[0].text

    def _fill_prompt_placeholders(self, prompt_template_string: str, language: str, code_sample: str) -> str:
        """
        Replaces placeholders in an existing prompt template string.
        """
        language_lowercase = language.lower()
        filled_prompt = prompt_template_string.replace("{{LANGUAGE}}", language)
        filled_prompt = filled_prompt.replace("{{LANGUAGE_LOWERCASE}}", language_lowercase)
        filled_prompt = filled_prompt.replace("{{CODE_SAMPLE}}", code_sample)
        return filled_prompt
