import json
import os
from typing import Dict
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from datetime import datetime
from tools.git_file_processor import GitFileProcessor
from tools.evaluate_code_file import CodeEvaluator
from utils.logger import logger
from utils.exceptions import (
    GitRepositoryError,
    APIError,
)

FILE_EXTENSION_MAP: Dict[str, str] = {
    ".py": "Python",
    ".java": "Java",
    ".groovy": "Java",
    ".kt": "Java",
    ".scala": "Java",
    ".go": "Go",
    ".rb": "Ruby",
    ".rs": "Rust",
    ".cs": "C#",
    ".cpp": "C++",
    ".cc": "C++",
    ".h": "C++",
    ".c": "C++",
    ".hpp": "C++",
    ".php": "PHP",
    ".tf": "Terraform",
    ".js": "JavaScript",
    ".ts": "JavaScript",  # TypeScript is normalized to Javascript.
    ".jsx": "JavaScript",
    ".tsx": "JavaScript",
    ".sh": "Unknown",
    ".yaml": "Unknown",
    ".xml": "Unknown",
}


class CodeProcessor:
    """
    Orchestrates the analysis of a single code file.

    This class is responsible for coordinating the entire analysis process for a
    given file. It fetches Git metadata, calls an external API for a detailed
    code evaluation, and then writes the combined results to a BigQuery table.
    """

    def __init__(self, settings, client, prompts, bigquery_repo=None):
        """
        Initializes the CodeProcessor.

        Args:
            settings: A configuration object with application settings.
            client: An initialized genai.Client instance.
            prompts: A dictionary containing pre-loaded prompt templates.
            bigquery_repo: A shared BigQueryRepository instance (optional).
        """
        self.settings = settings
        self.bigquery_repo = bigquery_repo
        self.git_processor = GitFileProcessor()
        self.api_url = settings.API_URL

        # Configure retry strategy
        self.session = requests.Session()
        retry_strategy = Retry(
            total=getattr(settings, "API_MAX_RETRIES", 3),
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["POST"],
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("https://", adapter)
        self.session.mount("http://", adapter)

        self.evaluator = CodeEvaluator(
            config=settings,
            client=client,
            system_instructions=prompts["system_instructions"],
            consolidated_eval_prompt=prompts["consolidated_eval"],
            json_conversion_prompt=prompts["json_conversion"],
        )



    def process_file(self, file_path, regen=False, gen=False):
        _, file_extension = os.path.splitext(file_path)
        language = FILE_EXTENSION_MAP.get(file_extension)

        if not language or language == "Unknown":
            return "skipped"

        git_info = self._get_git_info(file_path)

        if regen:
            logger.info(
                f"Regen is true, deleting existing records for {git_info['github_link']}"
            )
            self.bigquery_repo.delete(git_info["github_link"], git_info["last_updated"])
        elif self._is_already_processed(git_info):
            logger.info(f"{file_path} already processed and up-to-date, skipping.")
            return "skipped"

        code = self._read_raw_code(file_path)
        if "Error reading file" in code:
            logger.error(f"Could not read file {file_path}, skipping.")
            return "skipped"

        analysis_result = self._analyze_file(file_path, git_info, code)

        if analysis_result is None:
            return "skipped"

        bigquery_row = self._build_bigquery_row(
            analysis_result, file_path, code, gen
        )
        self._save_result(bigquery_row)
        return "processed"

    def _is_already_processed(self, git_info):
        """
        Checks if a file has already been processed and is up-to-date.

        This method checks for the existence of a record in BigQuery matching the
        file's GitHub link and last update timestamp.

        Args:
            git_info (dict): A dictionary containing Git metadata for the file.

        Returns:
            bool: True if the file has been processed and is current, False otherwise.
        """
        github_link = git_info["github_link"]
        last_updated = git_info.get("last_updated")
        return self.bigquery_repo.record_exists(github_link, last_updated)

    def _get_git_info(self, file_path):
        git_info = self.git_processor.execute(file_path)
        if "github_link" not in git_info:
            raise GitRepositoryError(f"File not in git repository: {file_path}")
        return git_info

    def _call_analysis_api(self, github_link, code, language):
        """
        Calls the external analysis API.

        This method sends the code and its GitHub link to the configured API endpoint
        and returns the JSON response. It includes error handling for network
        issues and non-successful HTTP status codes.

        Args:
            github_link (str): The URL of the file on GitHub.
            code (str): The raw source code of the file.
            language (str): The programming language of the file.

        Returns:
            dict: The JSON response from the API.

        Raises:
            APIError: If the API call fails.
        """
        headers = {"Content-Type": "application/json"}
        data = {"github_link": github_link, "code": code, "language": language}
        try:
            logger.info(f"Calling analysis API for {github_link}...")
            timeout = getattr(self.settings, "API_TIMEOUT", 90)
            response = self.session.post(
                self.api_url, headers=headers, json=data, timeout=timeout
            )
            logger.info(f"API returned status {response.status_code} for {github_link}")
            response.raise_for_status()  # Raises an HTTPError for bad responses (4xx or 5xx)
            return response.json()
        except requests.exceptions.Timeout:
            logger.error(f"API call timed out for {github_link}")
            raise APIError(f"API call timed out for {github_link}")
        except requests.exceptions.RequestException as e:
            logger.error(f"API call failed for {github_link}: {e}")
            raise APIError(f"API call failed for {github_link}: {e}")

    def _build_bigquery_row(self, analysis_result, file_path, code, gen=False):
        """
        Maps the combined analysis results and Git metadata into a flat dictionary
        that matches the BigQuery table schema.
        
        This method transforms semi-structured evaluation data (JSON) into a 
        format suitable for unnesting in the BigQuery view.
        """
        git_info = analysis_result.get("git_info", {})
        api_analysis = analysis_result.get("analysis", {})
        assessment_data = api_analysis.get("assessment", {})

        if not assessment_data:
            raise APIError(
                f"API response for {git_info.get('github_link')} is missing the 'assessment' object."
            )

        return {
            "github_link": git_info.get("github_link"),
            "file_path": file_path,
            "github_owner": git_info.get("github_owner"),
            "github_repo": git_info.get("github_repo"),
            "product_category": api_analysis.get("product_category"),
            "product_name": api_analysis.get("product_name"),
            "language": api_analysis.get("language"),
            "overall_compliance_score": assessment_data.get("overall_compliance_score"),
            "evaluation_data": json.dumps(assessment_data),
            "region_tags": api_analysis.get("region_tags"),
            "raw_code": code,
            "evaluation_date": datetime.now().isoformat(),
            "last_updated": git_info.get("last_updated"),
            "branch_name": git_info.get("branch_name"),
            "commit_history": json.dumps(git_info.get("commit_history")),
            "metadata": json.dumps(git_info.get("metadata")),
            "validation_details": json.dumps(analysis_result.get("validation_history")),
            "Generated": gen,
        }

    def _analyze_file(self, file_path, git_info, code):
        _, file_extension = os.path.splitext(file_path)
        language = FILE_EXTENSION_MAP.get(file_extension)
        github_link = git_info["github_link"]
        api_response = self._call_analysis_api(github_link, code, language)

        # Check for an error message from the API and skip the file if present.
        if "analysis" in api_response and "error" in api_response["analysis"]:
            error_message = api_response["analysis"]["error"]
            logger.info(f"Skipping file {github_link}: {error_message}")
            return None

        # Combine git_info with the API response to pass to build_bigquery_row
        combined_result = {"git_info": git_info, **api_response}
        return combined_result

    def _read_raw_code(self, file_path):
        try:
            with open(file_path, "r") as f:
                return f.read()
        except Exception as e:
            return f"Error reading file: {e}"

    def _save_result(self, row):
        self.bigquery_repo.create(row)

    def close(self):
        """
        No-op method for backward compatibility.
        
        The BigQuery connection is now managed externally and shared across
        all CodeProcessor instances. This method is kept for compatibility
        but does not close the connection.
        """
        pass

    def analyze_file_only(self, file_path):
        """
        Analyzes a single file without any database interaction, returning the full API response.
        """
        _, file_extension = os.path.splitext(file_path)
        language = FILE_EXTENSION_MAP.get(file_extension)

        if not language or language == "Unknown":
            return None

        git_info = self._get_git_info(file_path)
        github_link = git_info["github_link"]
        code = self._read_raw_code(file_path)
        if "Error reading file" in code:
            logger.error(f"Could not read file {file_path} for analysis.")
            return None
        return self._call_analysis_api(github_link, code, language)

    def categorize_file_only(self, file_path):
        """
        Analyzes a single file for product categorization only.
        """
        _, file_extension = os.path.splitext(file_path)
        language = FILE_EXTENSION_MAP.get(file_extension)

        if not language or language == "Unknown":
            return None

        git_info = self._get_git_info(file_path)
        github_link = git_info["github_link"]
        code = self._read_raw_code(file_path)
        if "Error reading file" in code:
            logger.error(f"Could not read file {file_path} for categorization.")
            return None
        api_response = self._call_analysis_api(github_link, code, language)

        api_analysis = api_response.get("analysis", {})

        return {
            "indexed_source_url": github_link,
            "region_tag": api_analysis.get("region_tags", [None])[0],
            "repository_name": git_info.get("github_repo"),
            "product_category": api_analysis.get("product_category"),
            "product_name": api_analysis.get("product_name"),
            "llm_determined": True,  # This is now always determined by the API
        }
