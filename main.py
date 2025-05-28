import argparse
import json
import subprocess
from tools.git_file_processor import get_git_data
from tools.evaluate_js_code_file import evaluate_code
from tools.js_analysis import extract_region_tags

def process_js_file(file_link):
    try:
        # Call git_file_processor.py
        
        git_info = get_git_data(file_link)
        print(git_info)

        js_info = extract_region_tags(file_link)
        print(js_info)

        style_info = evaluate_code(file_link)
        print(style_info)

        # Compose the results into a structured JSON


        # git_process = subprocess.run(['python', 'tools/git_file_processor.py', file_link], capture_output=True, text=True, check=True)
        # code = git_process.stdout.strip()
        # if "error" in code:
        #     return {"error": f"git_file_processor error: {code}"}

        # # Call js_eval.py
        # js_eval_process = subprocess.run(['python', 'tools/evaluate_js_code_file.py', file_link], input=code, capture_output=True, text=True, check=True)
        # js_eval_result = js_eval_process.stdout.strip()

        # # Call js_analysis.py
        # js_analysis_process = subprocess.run(['python', 'tools/js_analysis.py', file_link], input=code, capture_output=True, text=True, check=True)
        # js_analysis_result = js_analysis_process.stdout.strip()

        # Call code_analyzer.py
        #code_analyzer_process = subprocess.run(['python', 'tools/code_analyzer.py', file_link], input=code, capture_output=True, text=True, check=True)
        #code_analyzer_result = code_analyzer_process.stdout.strip()

        # Compose the results into a structured JSON
        result = {
            "git_file_processor": code,
            "js_eval": js_eval_result,
            "js_analysis": js_analysis_result
            #"code_analyzer": code_analyzer_result
        }
        return result

    except subprocess.CalledProcessError as e:
        return {"error": f"Subprocess error: {e.stderr}"}
    except Exception as e:
        return {"error": f"Error processing file: {e}"}

def main():
    parser = argparse.ArgumentParser(description="Process a JavaScript file from a link.")
    parser.add_argument("file_link", help="Link to the JavaScript file.")
    args = parser.parse_args()
    print(f"Processing file: {args.file_link}")
    result = process_js_file(args.file_link)
    #print(json.dumps(result, indent=4))

if __name__ == "__main__":
    main()
