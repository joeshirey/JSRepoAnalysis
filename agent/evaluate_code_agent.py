import os
import json
import vertexai
from vertexai.generative_models import GenerativeModel, Part, GenerationConfig
import adk

def fill_prompt_placeholders(prompt_template_string: str, language: str, code_sample: str) -> str:
    """
    Replaces placeholders in an existing prompt template string.

    Args:
        prompt_template_string (str): The prompt template as a string.
        language (str): The programming language (e.g., "Python", "Javascript").
        code_sample (str): The actual code sample to be evaluated.

    Returns:
        str: The prompt string with placeholders filled.
    """
    # Ensure the language casing for the code block is lowercase
    language_lowercase = language.lower()

    # Replace the placeholders
    # Order matters if placeholders could be substrings of each other (not the case here)
    filled_prompt = prompt_template_string.replace("{{LANGUAGE}}", language)
    filled_prompt = filled_prompt.replace("{{LANGUAGE_LOWERCASE}}", language_lowercase)
    filled_prompt = filled_prompt.replace("{{CODE_SAMPLE}}", code_sample)

    return filled_prompt

@adk.tool("evaluate_code_file")
def evaluate_code_file_tool(file_path: str, language: str) -> str:
    """
    Evaluates code using the Gemini 2.5 Flash model on Vertex AI.
    Args:
        file_path (str): The path to the code file to evaluate.
        language (str): The programming language of the code (e.g., "Python", "Javascript").
    Returns:
        str: A JSON string containing the evaluation result or an error message.
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            code_content = file.read()
    except FileNotFoundError:
        return json.dumps({"error": f"File not found at path: {file_path}"})
    except Exception as e:
        return json.dumps({"error": f"Error reading file: {e}"})

    # Read prompt from file
    # Adjust path for agent directory structure if necessary, assuming prompts are in the parent directory
    prompt_file_path = os.path.join(os.path.dirname(__file__), "../prompts/consolidated_eval.txt")
    try:
        with open(prompt_file_path, "r") as f:
            prompt_template = f.read()
    except FileNotFoundError:
        return json.dumps({"error": f"Prompt file not found at {prompt_file_path}."})
    except Exception as e:
        return json.dumps({"error": f"Error reading prompt file: {e}"})

    # Inject code into prompt
    prompt = fill_prompt_placeholders(prompt_template_string=prompt_template, language=language, code_sample=code_content)

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

    # Extract and clean the JSON response
    if response.candidates and response.candidates[0].content.parts:
        raw_text = response.candidates[0].content.parts[0].text
        # Attempt to remove markdown code block formatting
        if raw_text.startswith("```json"):
            cleaned_text = raw_text.removeprefix("```json").removesuffix("```").strip()
        elif raw_text.startswith("```"): # Fallback for generic code block
            cleaned_text = raw_text.removeprefix("```").removesuffix("```").strip()
        else:
            cleaned_text = raw_text.strip()
        return cleaned_text
    else:
        return json.dumps({"error": "No content generated or unexpected response structure."})

if __name__ == "__main__":
    adk.Agent.run()
