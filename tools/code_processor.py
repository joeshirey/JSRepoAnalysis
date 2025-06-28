import json
import os
import re
from datetime import datetime
from tools.git_file_processor import GitFileProcessor
from tools.extract_region_tags import RegionTagExtractor
from tools.firestore import FirestoreRepository
from strategies.strategy_factory import get_strategy
from utils.logger import logger
from utils.exceptions import UnsupportedFileTypeError, GitRepositoryError, NoRegionTagsError
from utils.data_classes import AnalysisResult
from dataclasses import asdict

class CodeProcessor:
    def __init__(self, settings):
        self.settings = settings
        self._firestore_repo = None
        self.git_processor = GitFileProcessor()
        self.tag_extractor = RegionTagExtractor()

    # Lazily initialize the Firestore repository to avoid connecting when not needed (e.g., --eval_only).
    @property
    def firestore_repo(self):
        if self._firestore_repo is None:
            self._firestore_repo = FirestoreRepository(self.settings)
        return self._firestore_repo

    def process_file(self, file_path, regen=False):
        strategy = get_strategy(file_path, self.settings)
        if not strategy:
            raise UnsupportedFileTypeError(f"Unsupported file type: {file_path}")

        git_info = self._get_git_info(file_path)
        document_id = self._get_document_id(git_info)
        collection_name = strategy.language

        if not regen and self._is_already_processed(collection_name, document_id, git_info):
            logger.info(f"{file_path} already processed and up-to-date, skipping.")
            return

        analysis_result = self._analyze_file(file_path, strategy, git_info)
        self._save_result(collection_name, document_id, analysis_result)

    def _get_git_info(self, file_path):
        git_info = self.git_processor.execute(file_path)
        if "github_link" not in git_info:
            raise GitRepositoryError(f"File not in git repository: {file_path}")
        return git_info

    def _get_document_id(self, git_info):
        github_link = git_info["github_link"]
        return github_link.replace("/", "_").replace(".", "_").replace(":", "_").replace("-", "_")

    def _is_already_processed(self, collection_name, document_id, git_info):
        existing_doc = self.firestore_repo.read(collection_name, document_id)
        return existing_doc and existing_doc.get('git_info', {}).get('last_updated') == git_info.get('last_updated')

    def _analyze_file(self, file_path, strategy, git_info):
        region_tags = self.tag_extractor.execute(file_path)
        if not region_tags:
            raise NoRegionTagsError("File not analyzed, no region tags")

        evaluation_data = self._evaluate_code(strategy, file_path, region_tags[0], git_info["github_link"])
        raw_code = self._read_raw_code(file_path)

        return AnalysisResult(
            git_info=git_info,
            region_tags=region_tags,
            evaluation_data=evaluation_data,
            raw_code=raw_code
        )

    def _evaluate_code(self, strategy, file_path, region_tag, github_link):
        style_info = strategy.evaluate_code(file_path, region_tag, github_link)
        logger.info(f"Style info received: {style_info}")
        
        # Use a regex to extract the JSON object from the response
        match = re.search(r"```json\s*({.*})\s*```", style_info, re.DOTALL)
        if match:
            cleaned_text = match.group(1)
        else:
            # Fallback for cases where the JSON is not in a code block
            cleaned_text = style_info.strip()

        logger.info(f"Cleaned text: {cleaned_text}")
        
        try:
            return json.loads(cleaned_text)
        except json.JSONDecodeError as e:
            logger.error(f"JSON parsing failed: {e}")
            logger.error(f"Malformed JSON text: {cleaned_text}")
            raise e

    def _read_raw_code(self, file_path):
        try:
            with open(file_path, 'r') as f:
                return f.read()
        except Exception as e:
            return f"Error reading file: {e}"

    def _save_result(self, collection_name, document_id, result):
        self.firestore_repo.create(collection_name, document_id, asdict(result))

    def close(self):
        if self._firestore_repo:
            self._firestore_repo.close()

    def analyze_file_only(self, file_path):
        """
        Analyzes a single file without any database interaction.
        """
        strategy = get_strategy(file_path, self.settings)
        if not strategy:
            raise UnsupportedFileTypeError(f"Unsupported file type: {file_path}")

        git_info = self._get_git_info(file_path)
        analysis_result = self._analyze_file(file_path, strategy, git_info)
        if analysis_result:
            return asdict(analysis_result)
        return None
