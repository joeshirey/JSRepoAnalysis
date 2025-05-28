import argparse
import json
import subprocess
from tools.git_file_processor import get_git_data
from tools.evaluate_js_code_file import evaluate_code
from tools.js_analysis import extract_region_tags

def process_js_file(file_link):
    #try:
    # Call git_file_processor.py
    
    git_info = get_git_data(file_link)
    #print(git_info)

    js_info = extract_region_tags(file_link)
    #print(js_info)

    style_info = evaluate_code(file_link)
    #print(style_info)

    result = {
        "git_info": git_info,
        "region_tags": js_info,
        "evaluation_data": json.loads(style_info)
    }

    return result

    #except subprocess.CalledProcessError as e:
    #    return {"error": f"Subprocess error: {e.stderr}"}
    #except Exception as e:
    #    return {"error": f"Error processing file: {e}"}

def main():
    parser = argparse.ArgumentParser(description="Process a JavaScript file from a link.")
    parser.add_argument("file_link", help="Link to the JavaScript file.")
    args = parser.parse_args()
    print(f"Processing file: {args.file_link}")
    result = process_js_file(args.file_link)
    print(json.dumps(result, indent=4))
    print(result["evaluation_data"]["overall_score"])

if __name__ == "__main__":
    main()
