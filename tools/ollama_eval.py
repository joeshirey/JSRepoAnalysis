import os
import json
import argparse
import ollama # Import ollama

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

def evaluate_code(file_path, language):
    """
    Evaluates code using the Ollama and gemma3 model.
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
    prompt = fill_prompt_placeholders(prompt_template_string=prompt_template, language=language, code_sample=code)
    #print(prompt)

    # Ollama configuration
    MODEL_NAME = "gemma3" # Hardcode model name for Ollama

    try:
        response = ollama.chat(
            model=MODEL_NAME,
            messages=[{'role': 'user', 'content': prompt}],
            options={
                'temperature': 0.1,
                'top_p': 0.9,
            }
        )
    except Exception as e:
        return json.dumps({"error": f"Error calling Ollama: {e}"})

    return response['message']['content']


def main():
    parser = argparse.ArgumentParser(description="Evaluate code file using Ollama and gemma3.")
    parser.add_argument("file_path", help="Path to the code file.")

    args = parser.parse_args()
    file_path = args.file_path
    style_info = None
    if file_path.endswith(('.js', '.ts')):
        style_info = evaluate_code(file_path, "Javascript")
    elif file_path.endswith('.py'):
        style_info = evaluate_code(file_path, "Python")
    else:
        return {"error": f"Unsupported file type for evaluation: {file_path}"}
    if style_info.startswith("```json"):
        cleaned_text = style_info.removeprefix("```json").removesuffix("```").strip()
    else:
        # Fallback for cases where it might just be wrapped in ```
        cleaned_text = style_info.strip().strip("`").strip()
    #evaluation_result = evaluate_code(file_path)
    print(cleaned_text)


if __name__ == "__main__":
    main()
