import os
import json
import argparse
import vertexai
import sys
from vertexai.generative_models import GenerativeModel, Part

def analyze_code(code):
    """
    Analyzes JavaScript code using the Gemini 2.5 Flash model on Vertex AI.
    """

    prompt = f"Analyze this code and summarize any potential issues, bugs, or areas for improvement:\\n\\n{code}"

    # Vertex AI configuration
    PROJECT_ID = os.environ.get("PROJECT_ID")  # Replace with your project ID
    LOCATION = "us-central1"  # Replace with your location
    MODEL_NAME = "gemini-2.5-flash-preview-05-20"

    # Initialize Vertex AI client
    vertexai.init(project=PROJECT_ID, location=LOCATION)
    model = GenerativeModel(MODEL_NAME)
    response = model.generate_content(prompt)

    if response.candidates and response.candidates[0].content.parts:
        return response.candidates[0].content.parts[0].text
    else:
        return "No content generated or unexpected response structure."


def main():
    parser = argparse.ArgumentParser(description="Analyze JavaScript code using Gemini 2.5 Flash on Vertex AI.")
    parser.add_argument("code", nargs="?", type=str, default=None, help="JavaScript code to analyze. If not provided, read from stdin.")

    args = parser.parse_args()

    if args.code is None:
        code = sys.stdin.read()
    else:
        code = args.code

    analysis_result = analyze_code(code)
    print(analysis_result)


if __name__ == "__main__":
    main()
