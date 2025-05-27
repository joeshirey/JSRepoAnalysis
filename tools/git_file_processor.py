import os
import subprocess
import json
import re

def get_github_owner_repo(file_path):
    """
    Gets the GitHub owner and repository name from the remote URL.
    """
    try:
        remote_url = subprocess.check_output(["git", "config", "--get", "remote.origin.url"], cwd=os.path.dirname(file_path)).decode("utf-8").strip()
        # Use regex to extract owner and repo
        match = re.search(r"github\.com(?:[:/]|@)(.*?)/(.*?)(?:\.git)?$", remote_url)
        if match:
            owner = match.group(1)
            repo = match.group(2)
            return owner, repo
        else:
            return None, None
    except subprocess.CalledProcessError:
        return None, None

def get_github_link(file_path):
    """
    Constructs the GitHub link for a given file.
    """
    try:
        owner, repo = get_github_owner_repo(file_path)
        if not owner or not repo:
            return None
        branch_name = get_branch_name(file_path)
        if not branch_name:
            return None
        relative_file_path = file_path.replace(os.getcwd() + "/", "")
        github_link = f"https://github.com/{owner}/{repo}/blob/{branch_name}/{relative_file_path}"
        return github_link
    except subprocess.CalledProcessError:
        return None

def get_branch_name(file_path):
    """
    Gets the current branch name.
    """
    try:
        branch_name = subprocess.check_output(["git", "rev-parse", "--abbrev-ref", "HEAD"], cwd=os.path.dirname(file_path)).decode("utf-8").strip()
        return branch_name
    except subprocess.CalledProcessError:
        return None

def get_commit_history(file_path):
    """
    Gets the commit history for a file and formats it as JSON.
    """
    try:
        git_log = subprocess.check_output(["git", "log", "--follow", "--pretty=format:%H%n%an%n%ae%n%ad%n%s", "--", file_path], cwd=os.path.dirname(file_path)).decode("utf-8")
        commits = []
        for commit in git_log.split("commit "):
            if commit:
                lines = commit.splitlines()
                if len(lines) >= 5:
                    commit_hash = lines[0]
                    author_name = lines[1]
                    author_email = lines[2]
                    date = lines[3]
                    message = lines[4]
                    commits.append({
                        "hash": commit_hash,
                        "author_name": author_name,
                        "author_email": author_email,
                        "date": date,
                        "message": message
                    })
        return commits
    except subprocess.CalledProcessError:
        return None

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

        owner, repo = get_github_owner_repo(file_path)
        branch_name = get_branch_name(file_path)
        github_link = get_github_link(file_path)
        commit_history = get_commit_history(file_path)

        # Get file metadata
        file_stats = os.stat(file_path)
        file_metadata = {
            "size": file_stats.st_size,
            "created": file_stats.st_ctime,
            "modified": file_stats.st_mtime,
        }

        # Combine git history and file metadata
        git_data = {
            "github_owner": owner,
            "github_repo": repo,
            "github_link": github_link,
            "branch_name": branch_name,
            "commit_history": commit_history,
            "metadata": file_metadata,
        }

        return git_data
    except subprocess.CalledProcessError as e:
        return {"error": f"Not a git repository or file not tracked by git: {e}"}
    except Exception as e:
        return {"error": str(e)}

if __name__ == '__main__':
    # Example usage:
    # Assuming this script is in the 'tools' directory.
    file_path = "tools/git_file_processor.py"
    git_info = get_git_data(file_path)
    print(json.dumps(git_info, indent=4))
