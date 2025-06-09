import os
import json
import argparse
import vertexai
from vertexai.generative_models import GenerativeModel, Part
import code

def evaluate_code(file_path):
    """
    Evaluates JavaScript code using the Gemini 2.5 Flash model on Vertex AI.
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
        with open("./prompts/js_eval.txt", "r") as f:
            prompt_template = f.read()
    except FileNotFoundError:
        return json.dumps({"error": "Prompt file not found."})
    except Exception as e:
        return json.dumps({"error": f"Error reading prompt file: {e}"})

    # Inject code into prompt
    prompt = prompt_template + code

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
    response = model.generate_content(prompt)

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
    parser = argparse.ArgumentParser(description="Evaluate JavaScript code file using Gemini 2.5 Flash on Vertex AI.")
    parser.add_argument("file_path", help="Path to the JavaScript code file.")

    args = parser.parse_args()
    file_path = args.file_path

    evaluation_result = evaluate_code(file_path)
    print(evaluation_result)


if __name__ == "__main__":
    main()
