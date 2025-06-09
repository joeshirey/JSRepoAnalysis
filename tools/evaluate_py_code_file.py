import os
import json
import argparse
import vertexai
from vertexai.generative_models import GenerativeModel, Part, GenerationConfig
import code

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

def evaluate_code(file_path):
    """
    Evaluates Python code using the Gemini 2.5 Flash model on Vertex AI.
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
        with open("../prompts/consolidated_eval.txt", "r") as f:
            prompt_template = f.read()
    except FileNotFoundError:
        return json.dumps({"error": "Prompt file not found."})
    except Exception as e:
        return json.dumps({"error": f"Error reading prompt file: {e}"})

    # Inject code into prompt
    prompt = fill_prompt_placeholders(prompt_template_string=prompt_template, language="Python", code_sample=code)
    #print(prompt)

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

    # prefix = "```json\n"
    # suffix = "\n```" # Assuming there's a newline before the closing backticks

    # if response.candidates and response.candidates[0].content.parts:
    #     temp_string = response.candidates[0].content.parts[0].text
    #     if temp_string.startswith("```json\n"):
    #         temp_string = temp_string.removeprefix("```json\n")
    #     elif temp_string.startswith("```json"): # In case there's no newline after ```json
    #         temp_string = temp_string.removeprefix("```json")

    #     if temp_string.endswith("\n```"):
    #         temp_string = temp_string.removesuffix("\n```")
    #     elif temp_string.endswith("```"):
    #         temp_string = temp_string.removesuffix("```")
    #     clean_json_string = temp_string.strip() 
    #     return clean_json_string
    # else:
    #     return "No content generated or unexpected response structure."



def main():
    parser = argparse.ArgumentParser(description="Evaluate Python code file using Gemini 2.5 Flash on Vertex AI.")
    parser.add_argument("file_path", help="Path to the Python code file.")

    args = parser.parse_args()
    file_path = args.file_path

    evaluation_result = evaluate_code(file_path)
    print(evaluation_result)


if __name__ == "__main__":
    main()
