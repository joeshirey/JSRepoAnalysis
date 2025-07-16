from .base_tool import BaseTool
import re
import sys
from utils.exceptions import RegionTagError


class RegionTagExtractor(BaseTool):
    def execute(self, file_path):
        """
        Extracts unique region tags from a file.
        """
        region_tags = set()
        try:
            if file_path == "-":
                file = sys.stdin
            else:
                file = open(file_path, "r", encoding="utf-8")
            with file:
                for line in file:
                    for match in re.finditer(
                        r"(?:#|\/\/)\s*\[(START|END)\s+(.+?)\]", line
                    ):
                        region_tag = match.group(2).strip()
                        region_tags.add(region_tag)
        except FileNotFoundError:
            raise RegionTagError(f"File not found at path: {file_path}")
        except Exception as e:
            raise RegionTagError(f"Error extracting region tags: {e}")

        return sorted(list(region_tags))
