
import re
import json
import argparse

import sys

def extract_region_tags(file_path):
    """
    Extracts unique region tags from a JavaScript or TypeScript file.
    """
    region_tags = set()
    try:
        if file_path == "-":
            file = sys.stdin
        else:
            file = open(file_path, 'r', encoding='utf-8')
        with file:
            for line in file:
                for match in re.finditer(r'\/\/\s*\[(START|END)\s+(.+?)\]', line):
                    region_tag = match.group(2).strip()
                    region_tags.add(region_tag)
    except FileNotFoundError:
        print(f"Error: File not found at path: {file_path}")
        return None
    except Exception as e:
        print(f"Error: An error occurred: {e}")
        return None

    return sorted(list(region_tags))


def main():
    parser = argparse.ArgumentParser(description="Extract region tags from a JavaScript/TypeScript file.")
    parser.add_argument("file_path", help="Path to the JavaScript/TypeScript file.")

    args = parser.parse_args()

    file_path = args.file_path

    region_tags = extract_region_tags(file_path)

    if region_tags is not None:
        try:
            print(region_tags)
        except Exception as e:
            print(f"Error: Failed to write to file: {e}")

if __name__ == "__main__":
    main()
