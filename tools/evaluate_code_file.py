from .base_tool import BaseTool
import json
import re
import time
from google import genai
from google.genai import types
from google.genai.types import Tool, GoogleSearch
from utils.exceptions import CodeEvaluatorError


class CodeEvaluator(BaseTool):
    """
    A tool for evaluating code samples using a large language model (LLM).

    This class encapsulates the logic for reading a code file, constructing a
    detailed prompt, and using a two-step LLM process to generate a structured
    JSON evaluation. The first LLM call performs the core analysis with web
    grounding, and the second call formats the analysis into a clean JSON object.
    """
    def __init__(self, config):
        self.config = config
        try:
            self.client = genai.Client()
            # System instructions are loaded from a file to guide the LLM's behavior.
            with open("./prompts/system_instructions.txt", "r") as f:
                self.system_instructions = f.read().splitlines()
        except Exception as e:
            raise CodeEvaluatorError(f"Error initializing genai.Client: {e}")

    def execute(self, file_path, language, region_tag, github_link):
        """
        Reads a code file and returns a JSON string with an LLM-driven evaluation.
        """
        try:
            with open(file_path, "r", encoding="utf-8") as file:
                code = file.read()
        except FileNotFoundError:
            raise CodeEvaluatorError(f"File not found at path: {file_path}")
        except Exception as e:
            raise CodeEvaluatorError(f"Error reading file: {e}")

        # The initial prompt is loaded from a template file.
        try:
            with open("./prompts/consolidated_eval.txt", "r") as f:
                prompt_template = f.read()
        except FileNotFoundError:
            raise CodeEvaluatorError("Prompt file not found.")
        except Exception as e:
            raise CodeEvaluatorError(f"Error reading prompt file: {e}")

        # The code and its metadata are injected into the prompt template.
        prompt = self._fill_prompt_placeholders(
            prompt_template_string=prompt_template,
            language=language,
            code_sample=code,
            github_link=github_link,
            region_tag=region_tag,
        )

        # The first LLM call uses Google Search as a grounding tool to ensure the
        # analysis is based on the most current and accurate information.
        grounding_tool = Tool(google_search=GoogleSearch())
        grounding_generation_config = types.GenerateContentConfig(
            temperature=0.0,
            system_instruction=self.system_instructions,
            tools=[grounding_tool],
        )

        try:
            response = self.client.models.generate_content(
                model=self.config.VERTEXAI_MODEL_NAME,
                contents=prompt,
                config=grounding_generation_config,
            )
            analysis_text = response.text
            time.sleep(1)
        except Exception as e:
            raise CodeEvaluatorError(f"Error generating content from Vertex AI: {e}")

        # The second LLM call is a formatting step. It takes the raw text analysis
        # from the first call and converts it into a structured JSON object.
        try:
            with open("./prompts/json_conversion.txt", "r") as f:
                json_prompt_template = f.read()
        except FileNotFoundError:
            raise CodeEvaluatorError("JSON conversion prompt file not found.")
        except Exception as e:
            raise CodeEvaluatorError(f"Error reading JSON conversion prompt file: {e}")

        json_prompt = json_prompt_template.replace("{{text}}", analysis_text)

        # Grounding is not needed for this second, simpler formatting task.
        json_generation_config = types.GenerateContentConfig(
            temperature=0.0,
            top_p=0.9,
            seed=5,
            system_instruction=self.system_instructions,
        )

        try:
            response = self.client.models.generate_content(
                model=self.config.VERTEXAI_MODEL_NAME,
                contents=json_prompt,
                config=json_generation_config,
            )
            time.sleep(1)
            return response.text
        except Exception as e:
            raise CodeEvaluatorError(f"Error converting analysis to JSON: {e}")

    def _fill_prompt_placeholders(
        self,
        prompt_template_string: str,
        language: str,
        code_sample: str,
        github_link: str,
        region_tag: str,
    ) -> str:
        """
        Injects dynamic values into the prompt template.

        This function takes the raw prompt template and populates it with the
        specific details of the code sample being evaluated, such as its
        language, source URL, and the code itself.
        """
        prompt = prompt_template_string.replace("{{language}}", language)
        prompt = prompt.replace("{{uri}}", github_link)
        prompt = prompt.replace("{{region_tag}}", region_tag)
        prompt = prompt.replace("{{code}}", code_sample)
        prompt = prompt.replace("{{cleaned_code}}", self.remove_comments(code_sample, language))
        return prompt

    def remove_comments(self, code: str, language: str) -> str:
        """
        Removes comments from a code string based on the language.
        """
        if language.lower() in ["python", "shell", "ruby"]:
            # Removes single-line comments starting with #
            return re.sub(r"#.*", "", code)
        elif language.lower() in ["javascript", "java", "c", "c++", "c#", "go", "swift", "typescript", "kotlin", "rust", "php"]:
            # Removes single-line // comments and multi-line /* ... */ comments
            code = re.sub(r"//.*", "", code)
            code = re.sub(r"/\*.*?\*/", "", code, flags=re.DOTALL)
            return code
        elif language.lower() in ["html", "xml"]:
            # Removes <!-- ... --> comments
            return re.sub(r"<!--.*?-->", "", code, flags=re.DOTALL)
        else:
            # Return original code if language is not supported
            return code