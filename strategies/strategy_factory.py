from .language_strategy import LanguageStrategy
import os


def get_strategy(file_path, config):
    """
    Returns the appropriate language strategy based on the file extension.
    """
    extension_to_language = {
        ".js": "JavaScript",
        ".jsx": "JavaScript",
        ".ts": "JavaScript",
        ".tsx": "JavaScript",
        ".py": "Python",
        ".java": "Java",
        ".go": "Go",
        ".rs": "Rust",
        ".rb": "Ruby",
        ".cs": "C#",
        ".cpp": "C++",
        ".h": "C++",
        ".hpp": "C++",
        ".c": "C++",
        ".php": "PHP",
        ".tf": "Terraform",
        ".sh": "Shell",
        ".yaml": "YAML",
        ".yml": "YAML",
        ".xml": "XML",
        ".json": "JSON",
        ".html": "HTML",
        ".css": "CSS",
    }

    file_extension = os.path.splitext(file_path)[1]
    language = extension_to_language.get(file_extension)

    if language in [
        "JavaScript",
        "Python",
        "Java",
        "Go",
        "Rust",
        "Ruby",
        "C#",
        "C++",
        "PHP",
        "Terraform",
    ]:
        return LanguageStrategy(config, language)
    else:
        return None
