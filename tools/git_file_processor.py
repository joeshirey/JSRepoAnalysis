import os
import subprocess
import json

def get_git_data(file_path):
    """
    Extracts git data from a file cloned from a git repository.

    Args:
        file_path (str): The path to the file.

    Returns:
        dict: A dictionary containing the git data, or an error message if the file is not from a git repository.
    \"\"\""""
    try:
        # Check if the file is part of a git repository
        subprocess.check_output(["git", "rev-parse", "--is-inside-work-tree"], cwd=os.path.dirname(file_path), stderr=subprocess.STDOUT)

        # Get git history for the file
        git_log = subprocess.check_output(["git", "log", "--follow", "--pretty=fuller", file_path], cwd=os.path.dirname(file_path)).decode("utf-8")

        # Get file metadata
        file_stats = os.stat(file_path)
        file_metadata = {
            "size": file_stats.st_size,
            "created": file_stats.st_ctime,
            "modified": file_stats.st_mtime,
        }

        # Combine git history and file metadata
        git_data = {
            "history": git_log,
            "metadata": file_metadata,
        }

        return git_data
    except subprocess.CalledProcessError as e:
        return {"error": f"Not a git repository or file not tracked by git: {e}"}
    except Exception as e:
        return {"error": str(e)}

if __name__ == '__main__':
    # Example usage:
    # Assuming this script is in the 'tools' directory and you want to process a file 'my_file.txt'
    # located in the parent directory.
    file_path = "../my_file.txt"  # Replace with the actual path to your file
    git_info = get_git_data(file_path)
    print(json.dumps(git_info, indent=4))
