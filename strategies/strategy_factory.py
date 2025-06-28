from .language_strategy import LanguageStrategy
import os

from .language_strategy import LanguageStrategy
import os

def get_strategy(file_path, config):
    """
    Returns the appropriate language strategy based on the file extension.
    """
    extension_to_language = {
        ".js": "Javascript",
        ".ts": "Javascript",
        ".py": "Python",
        ".java": "Java",
        ".go": "Go",
        ".rs": "Rust",
        ".rb": "Ruby",
        ".cs": "C#",
        ".cpp": "C++",
        ".h": "C++",
        ".hpp": "C++",
        ".php": "PHP"
    }
    
    file_extension = os.path.splitext(file_path)[1]
    language = extension_to_language.get(file_extension)
    
    if language:
        return LanguageStrategy(config, language)
    else:
        return None
