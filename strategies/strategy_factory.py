from .javascript_strategy import JavascriptStrategy
from .python_strategy import PythonStrategy

def get_strategy(file_path):
    """
    Returns the appropriate language strategy based on the file extension.
    """
    if file_path.endswith((".js", ".ts")):
        return JavascriptStrategy()
    elif file_path.endswith(".py"):
        return PythonStrategy()
    else:
        return None
