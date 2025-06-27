import json
import os
from datetime import datetime
from tools.git_file_processor import GitFileProcessor
from tools.extract_region_tags import RegionTagExtractor
from tools.firestore import create, read, FirestoreClient
from strategies.strategy_factory import get_strategy

class CodeProcessor:
    def __init__(self, db_name=None):
        self.firestore_client = FirestoreClient()
        self.db_name = db_name or os.getenv("FIRESTORE_DB")
        self.firestore_client.open_connection(db_name=self.db_name)
        self.git_processor = GitFileProcessor()
        self.tag_extractor = RegionTagExtractor()

    def process_file(self, file_path, regen=False):
        strategy = get_strategy(file_path)
        if not strategy:
            print(f"Skipping processing for unsupported file type: {file_path}")
            return {"error": f"Unsupported file type: {file_path}"}

        git_info = self.git_processor.execute(file_path)
        if "github_link" not in git_info:
            print(f"Skipping processing for file not in git repository: {file_path}")
            return {"error": f"File not in git repository: {file_path}"}

        github_link = git_info["github_link"]
        document_id = github_link.replace("/", "_").replace(".", "_").replace(":", "_").replace("-", "_")

        if not regen:
            existing_doc = read(strategy.__class__.__name__.replace("Strategy", ""), document_id)
            if existing_doc and existing_doc.get('git_info', {}).get('last_updated') == git_info.get('last_updated'):
                print(f"{file_path} already processed and up-to-date, skipping.")
                return existing_doc

        region_tags = self.tag_extractor.execute(file_path)
        if not region_tags:
            evaluation_data = {"error": "File not analyzed, no region tags"}
        else:
            style_info = strategy.evaluate_code(file_path)
            if style_info.startswith("```json"):
                cleaned_text = style_info.removeprefix("```json").removesuffix("```").strip()
            else:
                cleaned_text = style_info.strip().strip("`").strip()
            evaluation_data = json.loads(cleaned_text)

        try:
            with open(file_path, 'r') as f:
                raw_code = f.read()
        except Exception as e:
            raw_code = f"Error reading file: {e}"

        result = {
            "git_info": git_info,
            "region_tags": region_tags,
            "evaluation_data": evaluation_data,
            "raw_code": raw_code,
            "evaluation_date": datetime.now().strftime("%Y-%m-%d %H:%M")
        }
        create(strategy.__class__.__name__.replace("Strategy", ""), document_id, result)
        return result

    def close(self):
        self.firestore_client.close_connection()
