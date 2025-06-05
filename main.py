import argparse
import json
import subprocess
import os
from datetime import datetime
from tools.git_file_processor import get_git_data
#from tools.evaluate_js_code_file import evaluate_code as evaluate_js_code
#from tools.evaluate_py_code_file import evaluate_code as evaluate_py_code
from tools.evaluate_code_file import evaluate_code
from tools.extract_region_tags import extract_region_tags
from tools.firestore import create
from dotenv import load_dotenv




def process_file(file_link):
    #try:
    # Call git_file_processor.py
    
    git_info = get_git_data(file_link)
    #print(git_info)

    js_info = extract_region_tags(file_link)
    #print(js_info)

    try:
        if not js_info:
            cleaned_text = '["File not analyzed, no region tags"]'
        else:
            style_info = None
            if file_link.endswith(('.js', '.ts')):
                style_info = evaluate_code(file_link, "TypeScript")
            elif file_link.endswith('.py'):
                style_info = evaluate_code(file_link, "Python")
            else:
                return {"error": f"Unsupported file type for evaluation: {file_link}"}
            if style_info.startswith("```json"):
                cleaned_text = style_info.removeprefix("```json").removesuffix("```").strip()
            else:
                # Fallback for cases where it might just be wrapped in ```
                cleaned_text = style_info.strip().strip("`").strip()
    
        result = {
            "git_info": git_info,
            "region_tags": js_info,
            "evaluation_data": json.loads(cleaned_text),
            "evaluation_date": datetime.now().strftime("%Y-%m-%d %H:%M")
        }

    except Exception as e:
        error_message = f"Error processing file: {e}"
        absolute_path = os.path.abspath(file_link)
        with open("errors.log", "a") as error_file:
            error_file.write(f"{absolute_path}\t{error_message}\n")
        return {"error": error_message}


    # Determine language for collection name
    language = None
    if file_link.endswith(('.js', '.ts')):
        language = "Javascript"
    elif file_link.endswith('.py'):
        language = "Python"

    # Write to Firestore if git info and language are available
    if "git_info" in result and "github_link" in result["git_info"] and language:
        github_link = result["git_info"]["github_link"]
        # Use github_link as document_id, replace characters not allowed in Firestore document IDs
        document_id = github_link.replace("/", "_").replace(".", "_").replace(":", "_").replace("-", "_") # Example replacement, adjust as needed
        create(language, document_id, result)
    elif not language:
        print(f"Skipping Firestore write for unsupported file type: {file_link}")
    else:
        print(f"Skipping Firestore write for file not in git repository: {file_link}")

    return result

    #except subprocess.CalledProcessError as e:
    #    return {"error": f"Subprocess error: {e.stderr}"}
    #except Exception as e:
    #    return {"error": f"Error processing file: {e}"}



def main():
    load_dotenv()
    parser = argparse.ArgumentParser(description="Process a code file or directory.")
    parser.add_argument("file_link", help="Path to the code file or directory.")
    args = parser.parse_args()

    input_path = args.file_link

    if os.path.isfile(input_path):
        print(f"Processing file: {input_path}")
        result = process_file(input_path)
        #print(json.dumps(result, indent=4))
    elif os.path.isdir(input_path):
        print(f"Processing directory: {input_path}")
        for root, dirs, files in os.walk(input_path):
            for file in files:
                file_path = os.path.join(root, file)
                if file_path.endswith(('.js', '.ts', '.py')):
                    print(f"Processing file: {file_path}")
                    result = process_file(file_path)
                    #print(json.dumps(result, indent=4))
    else:
        print(f"Error: Invalid path provided: {input_path}")


if __name__ == "__main__":
    main()
