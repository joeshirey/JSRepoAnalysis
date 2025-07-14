from .language_strategy import LanguageStrategy
import os

def get_strategy(file_path, config):
    """
    Returns the appropriate language strategy based on the file extension.
    """
    extension_to_language = {
        ".js": "javascript",
        ".jsx": "javascript",
        ".ts": "javascript",
        ".tsx": "javascript",
        ".py": "python",
        ".java": "java",
        ".go": "go",
        ".rs": "rust",
        ".rb": "ruby",
        ".cs": "csharp",
        ".cpp": "cpp",
        ".h": "cpp",
        ".hpp": "cpp",
        ".php": "php"
    }
    
    file_extension = os.path.splitext(file_path)[1]
    language = extension_to_language.get(file_extension)
    
    if language:
        return LanguageStrategy(config, language)
    else:
        return None
