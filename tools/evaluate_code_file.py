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
            with open("./prompts/system_instructions.txt", "r") as f:
                system_instructions = f.read()
            self.model = GenerativeModel(self.config.VERTEXAI_MODEL_NAME, system_instruction=system_instructions)
        except Exception as e:
            raise CodeEvaluatorError(f"Error initializing Vertex AI: {e}")

    def execute(self, file_path, language, region_tag, github_link):
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
        prompt = self._fill_prompt_placeholders(prompt_template_string=prompt_template, language=language, code_sample=code, github_link=github_link, region_tag=region_tag)

        # Configure generation parameters for consistent output.
        generation_config = GenerationConfig(
            temperature=0.0,
            top_p=0.9,
        )

        try:
            response = self.model.generate_content(
                prompt,
                generation_config=generation_config
            )
            analysis_text = response.candidates[0].content.parts[0].text
        except Exception as e:
            raise CodeEvaluatorError(f"Error generating content from Vertex AI: {e}")

        # Convert the analysis text to JSON
        try:
            with open("./prompts/json_conversion.txt", "r") as f:
                json_prompt_template = f.read()
        except FileNotFoundError:
            raise CodeEvaluatorError("JSON conversion prompt file not found.")
        except Exception as e:
            raise CodeEvaluatorError(f"Error reading JSON conversion prompt file: {e}")

        json_prompt = json_prompt_template.replace("{{text}}", analysis_text)

        try:
            response = self.model.generate_content(
                json_prompt,
                generation_config=generation_config
            )
            return response.candidates[0].content.parts[0].text
        except Exception as e:
            raise CodeEvaluatorError(f"Error converting analysis to JSON: {e}")


    def _fill_prompt_placeholders(self, prompt_template_string: str, language: str, code_sample: str, github_link: str, region_tag: str) -> str:
        """
        Replaces placeholders in an existing prompt template string.
        """
        language_lowercase = language.lower()
        prompt = f"**LANGUAGE:**\n{language}\n\n"
        prompt += f"**URI:**\n{github_link}\n\n"
        prompt += f"**Region Tag ID:**\n{region_tag}\n\n"
        prompt += f"**CODE_SAMPLE:**\n```{language_lowercase}\n{json.dumps(code_sample)}\n```"
        return prompt

