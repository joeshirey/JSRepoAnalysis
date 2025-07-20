from .base_tool import BaseTool
import json
import re
from google import genai
from google.genai import types
from google.genai.types import Tool, GoogleSearch
from utils.exceptions import CodeEvaluatorError


class CodeEvaluator(BaseTool):
    def __init__(self, config):
        self.config = config
        try:
            self.client = genai.Client()
            with open("./prompts/system_instructions.txt", "r") as f:
                self.system_instructions = f.read().splitlines()
        except Exception as e:
            raise CodeEvaluatorError(f"Error initializing genai.Client: {e}")

    def execute(self, file_path, language, region_tag, github_link):
        """
        Evaluates code using the Gemini 2.5 Flash model on Vertex AI.
        """
        try:
            with open(file_path, "r", encoding="utf-8") as file:
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
        prompt = self._fill_prompt_placeholders(
            prompt_template_string=prompt_template,
            language=language,
            code_sample=code,
            github_link=github_link,
            region_tag=region_tag,
        )

        # Configure generation parameters for the first call with grounding.
        grounding_tool = Tool(google_search=GoogleSearch())
        grounding_generation_config = types.GenerateContentConfig(
            temperature=0.0,
            top_p=0.9,
            system_instruction=self.system_instructions,
            tools=[grounding_tool],
        )

        citation_sources = []
        try:
            response = self.client.models.generate_content(
                model=self.config.VERTEXAI_MODEL_NAME,
                contents=prompt,
                config=grounding_generation_config,
            )
            analysis_text = response.text
            if hasattr(response, "citation_metadata") and response.citation_metadata:
                for source in response.citation_metadata.citation_sources:
                    if source.uri:
                        citation_sources.append(source.uri)

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

        if citation_sources:
            references_json_string = json.dumps(citation_sources)
            json_prompt += f"""
\n**Additional Instructions:**
6.  The JSON object MUST also include a top-level key named `references`.
7.  The value for the `references` key MUST be the following JSON array of strings:
    {references_json_string}
"""

        # Configure generation parameters for the second call without grounding.
        json_generation_config = types.GenerateContentConfig(
            temperature=0.0,
            top_p=0.9,
            system_instruction=self.system_instructions,
        )

        try:
            response = self.client.models.generate_content(
                model=self.config.VERTEXAI_MODEL_NAME,
                contents=json_prompt,
                config=json_generation_config,
            )
            # Parse the JSON string from the model
            evaluation_dict = json.loads(response.text)
            
            # Add references if they exist
            if citation_sources:
                evaluation_dict['references'] = citation_sources
            
            return evaluation_dict
        except (json.JSONDecodeError, Exception) as e:
            # Attempt to fix the JSON using a lenient parser
            try:
                import demjson3
                cleaned_text = response.text.strip()
                match = re.search(r"```json\s*({.*})\s*```", cleaned_text, re.DOTALL)
                if match:
                    cleaned_text = match.group(1)
                
                evaluation_dict = demjson3.decode(cleaned_text)
                if citation_sources:
                    evaluation_dict['references'] = citation_sources
                return evaluation_dict
            except Exception as e2:
                 raise CodeEvaluatorError(f"Error converting analysis to JSON or adding references: {e} - {e2}")

    def _fill_prompt_placeholders(
        self,
        prompt_template_string: str,
        language: str,
        code_sample: str,
        github_link: str,
        region_tag: str,
    ) -> str:
        """
        Replaces placeholders in an existing prompt template string.
        """
        language_lowercase = language.lower()
        prompt = f"**LANGUAGE:**\n{language}\n\n"
        prompt += f"**URI:**\n{github_link}\n\n"
        prompt += f"**Region Tag ID:**\n{region_tag}\n\n"
        prompt += (
            f"**CODE_SAMPLE:**\n```{language_lowercase}\n{json.dumps(code_sample)}\n```"
        )
        return prompt
