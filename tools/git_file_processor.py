from .base_tool import BaseTool
import os
import subprocess
import json
import re
from datetime import datetime

class GitFileProcessor(BaseTool):
    def execute(self, file_path):
        """
        Extracts git data from a file cloned from a git repository.
        """
        try:
            # Check if the file is part of a git repository
            subprocess.check_output(["git", "rev-parse", "--is-inside-work-tree"], cwd=os.path.dirname(file_path), stderr=subprocess.STDOUT)

            owner, repo = self._get_github_owner_repo(file_path)
            branch_name = self._get_branch_name(file_path)
            github_link = self._get_github_link(file_path, owner, repo, branch_name)
            commit_history = self._get_commit_history(file_path)

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
                "last_updated": datetime.strptime(commit_history[0]["date"], '%a %b %d %H:%M:%S %Y %z').strftime('%Y-%m-%d') if commit_history else None,
                "commit_history": commit_history,
                "metadata": file_metadata,
            }

            return git_data
        except subprocess.CalledProcessError as e:
            return {"error": f"Not a git repository or file not tracked by git: {e}"}
        except Exception as e:
            return {"error": str(e)}

    def _get_github_owner_repo(self, file_path):
        """
        Gets the GitHub owner and repository name from the remote URL.
        """
        try:
            remote_url = subprocess.check_output(["git", "config", "--get", "remote.origin.url"], cwd=os.path.dirname(file_path)).decode("utf-8").strip()
            match = re.search(r"github\.com(?:[:/]|@)(.*?)/(.*?)(?:\.git)?$", remote_url)
            if match:
                owner = match.group(1)
                repo = match.group(2)
                return owner, repo
            else:
                return None, None
        except subprocess.CalledProcessError:
            return None, None

    def _get_github_link(self, file_path, owner, repo, branch_name):
        """
        Constructs the GitHub link for a given file.
        """
        try:
            if not owner or not repo or not branch_name:
                return None
            git_root = subprocess.check_output(["git", "rev-parse", "--show-toplevel"], cwd=os.path.dirname(file_path)).decode("utf-8").strip()
            relative_file_path = os.path.relpath(file_path, git_root)
            github_link = f"https://github.com/{owner}/{repo}/blob/{branch_name}/{relative_file_path}"
            return github_link
        except subprocess.CalledProcessError:
            return None

    def _get_branch_name(self, file_path):
        """
        Gets the current branch name.
        """
        try:
            branch_name = subprocess.check_output(["git", "rev-parse", "--abbrev-ref", "HEAD"], cwd=os.path.dirname(file_path)).decode("utf-8").strip()
            return branch_name
        except subprocess.CalledProcessError:
            return None

    def _get_commit_history(self, file_path):
        """
        Gets the commit history for a file and formats it as JSON.
        """
        try:
            git_root = subprocess.check_output(["git", "rev-parse", "--show-toplevel"], cwd=os.path.dirname(file_path)).decode("utf-8").strip()
            git_log = subprocess.check_output(["git", "log", "--follow", "--pretty=format:%H%n%an%n%ae%n%ad%n%s%n", "--", file_path], cwd=git_root).decode("utf-8")
            commits = []
            log_lines = git_log.strip().split('\n')
            i = 0
            while i + 4 < len(log_lines):
                commit_hash = log_lines[i].strip()
                author_name = log_lines[i+1].strip()
                author_email = log_lines[i+2].strip()
                date = log_lines[i+3].strip()
                message = log_lines[i+4].strip()

                commits.append({
                    "hash": commit_hash,
                    "author_name": author_name,
                    "author_email": author_email,
                    "date": date,
                    "message": message
                })
                i += 5
            return commits
        except subprocess.CalledProcessError as e:
            print(f"Error getting commit history: {e}")
            return None
