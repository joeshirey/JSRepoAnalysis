import json
import re
import demjson3
from datetime import datetime
from tools.git_file_processor import GitFileProcessor
from tools.extract_region_tags import RegionTagExtractor
from tools.bigquery import BigQueryRepository
from tools.extract_product_info import categorize_sample
from strategies.strategy_factory import get_strategy
from utils.logger import logger
from utils.exceptions import (
    UnsupportedFileTypeError,
    GitRepositoryError,
    NoRegionTagsError,
)
from utils.data_classes import AnalysisResult
from dataclasses import asdict


class CodeProcessor:
    def __init__(self, settings):
        self.settings = settings
        self._bigquery_repo = None
        self.git_processor = GitFileProcessor()
        self.tag_extractor = RegionTagExtractor()

    @property
    def bigquery_repo(self):
        if self._bigquery_repo is None:
            self._bigquery_repo = BigQueryRepository(self.settings)
        return self._bigquery_repo

    def process_file(self, file_path, regen=False):
        strategy = get_strategy(file_path, self.settings)
        if not strategy:
            raise UnsupportedFileTypeError(f"Unsupported file type: {file_path}")

        git_info = self._get_git_info(file_path)

        if regen:
            logger.info(
                f"Regen is true, deleting existing records for {git_info['github_link']}"
            )
            self.bigquery_repo.delete(git_info["github_link"], git_info["last_updated"])
        elif self._is_already_processed(git_info):
            logger.info(f"{file_path} already processed and up-to-date, skipping.")
            return "skipped"

        analysis_result = self._analyze_file(file_path, strategy, git_info)

        bigquery_row = self._build_bigquery_row(
            analysis_result, strategy.language, file_path
        )
        self._save_result(bigquery_row)
        return "processed"

    def _is_already_processed(self, git_info):
        github_link = git_info["github_link"]
        last_updated = git_info.get("last_updated")

        # Convert last_updated string to date object if it's not None
        if last_updated:
            last_updated_dt = datetime.strptime(last_updated, "%Y-%m-%d").date()
        else:
            last_updated_dt = None

        existing_record = self.bigquery_repo.read(github_link)

        if (
            existing_record
            and "last_updated" in existing_record
            and existing_record["last_updated"]
        ):
            # Ensure existing_record['last_updated'] is a date object for comparison
            if isinstance(existing_record["last_updated"], datetime):
                existing_last_updated_dt = existing_record["last_updated"].date()
            else:
                # Assuming it's a string in 'YYYY-MM-DD' format
                existing_last_updated_dt = datetime.strptime(
                    str(existing_record["last_updated"]), "%Y-%m-%d"
                ).date()

            return existing_last_updated_dt == last_updated_dt

        return False

    def _get_git_info(self, file_path):
        git_info = self.git_processor.execute(file_path)
        if "github_link" not in git_info:
            raise GitRepositoryError(f"File not in git repository: {file_path}")
        return git_info

    def _build_bigquery_row(self, analysis_result, language, file_path):
        git_info = analysis_result.git_info
        evaluation_data = analysis_result.evaluation_data

        return {
            "github_link": git_info.get("github_link"),
            "file_path": file_path,
            "github_owner": git_info.get("github_owner"),
            "github_repo": git_info.get("github_repo"),
            "product_category": evaluation_data.get("product_category"),
            "product_name": evaluation_data.get("product_name"),
            "language": language,
            "overall_compliance_score": evaluation_data.get("overall_compliance_score"),
            "evaluation_data": json.dumps(evaluation_data),
            "region_tags": analysis_result.region_tags,
            "raw_code": analysis_result.raw_code,
            "evaluation_date": analysis_result.evaluation_date,
            "last_updated": git_info.get("last_updated"),
            "branch_name": git_info.get("branch_name"),
            "commit_history": json.dumps(git_info.get("commit_history")),
            "metadata": json.dumps(git_info.get("metadata")),
        }

    def _analyze_file(self, file_path, strategy, git_info):
        region_tags = self.tag_extractor.execute(file_path)
        if not region_tags:
            raise NoRegionTagsError("File not analyzed, no region tags")

        # First, evaluate the code as before to get the LLM's analysis
        evaluation_data = self._evaluate_code(
            strategy, file_path, region_tags[0], git_info["github_link"]
        )
        raw_code = self._read_raw_code(file_path)

        # Now, use the new, more reliable product categorization logic
        row_data = {
            "indexed_source_url": git_info.get("github_link"),
            "region_tag": region_tags[0] if region_tags else "",
            "repository_name": git_info.get("github_repo"),
        }
        product_category, product_name, llm_determined = categorize_sample(
            row_data, raw_code, llm_fallback=True
        )

        # Update the evaluation data with the new product info, overwriting
        # whatever the LLM might have provided for these specific fields.
        evaluation_data["product_category"] = product_category
        evaluation_data["product_name"] = product_name
        evaluation_data["llm_determined"] = llm_determined

        return AnalysisResult(
            git_info=git_info,
            region_tags=region_tags,
            evaluation_data=evaluation_data,
            raw_code=raw_code,
        )

    def _evaluate_code(self, strategy, file_path, region_tag, github_link):
        style_info = strategy.evaluate_code(file_path, region_tag, github_link)

        match = re.search(r"```json\s*({.*})\s*```", style_info, re.DOTALL)
        if match:
            cleaned_text = match.group(1)
        else:
            cleaned_text = style_info.strip()

        cleaned_text = re.sub(r",\s*([\]}])", r"\1", cleaned_text)

        try:
            return json.loads(cleaned_text)
        except json.JSONDecodeError as e:
            logger.warning(
                f"Initial JSON parsing failed: {e}. Attempting to fix with lenient parser."
            )
            try:
                return demjson3.decode(cleaned_text)
            except demjson3.JSONDecodeError as e2:
                logger.error(f"JSON parsing failed even with lenient parser: {e2}")
                logger.error(f"Malformed JSON text: {cleaned_text}")
                raise e2


    def _read_raw_code(self, file_path):
        try:
            with open(file_path, "r") as f:
                return f.read()
        except Exception as e:
            return f"Error reading file: {e}"

    def _save_result(self, row):
        self.bigquery_repo.create(row)

    def categorize_file_only(self, file_path):
        """
        Analyzes a single file for product categorization only.
        """
        git_info = self._get_git_info(file_path)
        region_tags = self.tag_extractor.execute(file_path)
        if not region_tags:
            return None

        raw_code = self._read_raw_code(file_path)
        row_data = {
            "indexed_source_url": git_info.get("github_link"),
            "region_tag": region_tags[0],
            "repository_name": git_info.get("github_repo"),
        }
        product_category, product_name, llm_determined = categorize_sample(
            row_data, raw_code, llm_fallback=True
        )

        return {
            "indexed_source_url": git_info.get("github_link"),
            "region_tag": region_tags[0],
            "repository_name": git_info.get("github_repo"),
            "product_category": product_category,
            "product_name": product_name,
            "llm_determined": llm_determined,
        }

    def close(self):
        if self._bigquery_repo:
            self._bigquery_repo.close()
