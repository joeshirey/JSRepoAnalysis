import argparse
import json
import subprocess
from tools.git_file_processor import get_git_data
from tools.evaluate_js_code_file import evaluate_code as evaluate_js_code
from tools.evaluate_py_code_file import evaluate_code as evaluate_py_code
from tools.extract_region_tags import extract_region_tags

def process_file(file_link):
    #try:
    # Call git_file_processor.py
    
    git_info = get_git_data(file_link)
    #print(git_info)

    js_info = extract_region_tags(file_link)
    #print(js_info)

    style_info = None
    if file_link.endswith(('.js', '.ts')):
        style_info = evaluate_js_code(file_link)
    elif file_link.endswith('.py'):
        style_info = evaluate_py_code(file_link)
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
        "evaluation_data": json.loads(cleaned_text)
    }

    return result

    #except subprocess.CalledProcessError as e:
    #    return {"error": f"Subprocess error: {e.stderr}"}
    #except Exception as e:
    #    return {"error": f"Error processing file: {e}"}

def main():
    parser = argparse.ArgumentParser(description="Process a code file from a link.")
    parser.add_argument("file_link", help="Link to the code file.")
    args = parser.parse_args()
    print(f"Processing file: {args.file_link}")
    result = process_file(args.file_link)
    print(json.dumps(result, indent=4))
    if "evaluation_data" in result and "overall_score" in result["evaluation_data"]:
        print(result["evaluation_data"]["overall_score"])
    elif "error" in result:
        print(f"Error processing file: {result['error']}")

if __name__ == "__main__":
    main()
