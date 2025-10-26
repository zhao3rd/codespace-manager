"""
GitHub-based Persistent Storage for Keepalive Tasks
Uses GitHub API to store data in a private repository
"""
import requests
import json
import base64
from typing import Dict, Optional
from datetime import datetime


class GitHubStorage:
    """Store keepalive tasks in GitHub repository"""
    
    def __init__(self, token: str, repo: str, branch: str = "main"):
        """
        Initialize GitHub storage
        
        Args:
            token: GitHub Personal Access Token
            repo: Repository in format "owner/repo"
            branch: Branch name (default: main)
        """
        self.token = token
        self.repo = repo
        self.branch = branch
        self.base_url = "https://api.github.com"
        self.file_path = "codespace-manager/keepalive_tasks.json"  # Store in subdirectory
        self.headers = {
            "Authorization": f"token {token}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28"
        }
        self.max_retries = 3  # Maximum retry attempts for conflict resolution
    
    def _get_file_sha(self) -> Optional[str]:
        """Get current file SHA for updates"""
        url = f"{self.base_url}/repos/{self.repo}/contents/{self.file_path}"
        params = {"ref": self.branch}
        
        try:
            response = requests.get(url, headers=self.headers, params=params)
            if response.status_code == 200:
                return response.json().get("sha")
            return None
        except Exception:
            return None
    
    def _merge_tasks(self, remote_tasks: Dict, local_tasks: Dict) -> Dict:
        """
        Merge remote and local tasks, keeping the most recent data
        
        Args:
            remote_tasks: Tasks from GitHub
            local_tasks: Tasks to save
            
        Returns:
            Merged tasks dictionary
        """
        merged = remote_tasks.copy()
        
        # Update with local tasks (local tasks take priority)
        for key, task in local_tasks.items():
            merged[key] = task
        
        return merged
    
    def save_tasks(self, tasks: Dict) -> bool:
        """
        Save keepalive tasks to GitHub with conflict resolution
        
        Args:
            tasks: Dictionary of keepalive tasks
            
        Returns:
            True if successful
        """
        for attempt in range(self.max_retries):
            try:
                # Convert datetime objects to ISO format strings
                serializable_tasks = {}
                for key, task in tasks.items():
                    serializable_tasks[key] = {
                        'account_name': task['account_name'],
                        'cs_name': task['cs_name'],
                        'start_time': task['start_time'].isoformat(),
                        'keepalive_hours': task['keepalive_hours']
                    }
                
                # Get current file SHA and content if exists
                sha = self._get_file_sha()
                
                # If this is a retry, merge with remote data
                if attempt > 0 and sha:
                    remote_tasks = self.load_tasks()
                    if remote_tasks:
                        # Merge remote and local tasks
                        merged_data = {}
                        for key, task in remote_tasks.items():
                            merged_data[key] = {
                                'account_name': task['account_name'],
                                'cs_name': task['cs_name'],
                                'start_time': task['start_time'].isoformat(),
                                'keepalive_hours': task['keepalive_hours']
                            }
                        # Local tasks override remote
                        merged_data.update(serializable_tasks)
                        serializable_tasks = merged_data
                
                # Convert to JSON and encode to base64
                content = json.dumps(serializable_tasks, indent=2)
                encoded_content = base64.b64encode(content.encode()).decode()
                
                # Prepare request
                url = f"{self.base_url}/repos/{self.repo}/contents/{self.file_path}"
                
                # Generate commit message with task count
                task_count = len(serializable_tasks)
                timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                data = {
                    "message": f"[Auto] Update keepalive tasks ({task_count} active) - {timestamp}",
                    "content": encoded_content,
                    "branch": self.branch
                }
                
                if sha:
                    data["sha"] = sha
                
                # Create or update file (GitHub API auto-creates directories)
                response = requests.put(url, headers=self.headers, json=data)
                
                if response.status_code in [200, 201]:
                    return True
                elif response.status_code == 409:
                    # Conflict: file was modified by someone else, retry
                    print(f"Conflict detected on attempt {attempt + 1}, retrying...")
                    continue
                else:
                    print(f"GitHub API error {response.status_code}: {response.text}")
                    return False
                    
            except Exception as e:
                print(f"Error saving to GitHub (attempt {attempt + 1}): {e}")
                if attempt == self.max_retries - 1:
                    return False
        
        print(f"Failed to save after {self.max_retries} attempts")
        return False
    
    def load_tasks(self) -> Dict:
        """
        Load keepalive tasks from GitHub
        
        Returns:
            Dictionary of keepalive tasks
        """
        url = f"{self.base_url}/repos/{self.repo}/contents/{self.file_path}"
        params = {"ref": self.branch}
        
        try:
            response = requests.get(url, headers=self.headers, params=params)
            
            if response.status_code == 404:
                # File doesn't exist yet
                return {}
            
            if response.status_code != 200:
                return {}
            
            # Decode content from base64
            content = response.json().get("content", "")
            decoded_content = base64.b64decode(content).decode()
            serializable_tasks = json.loads(decoded_content)
            
            # Convert ISO format strings back to datetime objects
            tasks = {}
            current_time = datetime.now()
            
            for key, task in serializable_tasks.items():
                start_time = datetime.fromisoformat(task['start_time'])
                keepalive_hours = task['keepalive_hours']
                
                # Calculate elapsed time
                elapsed_hours = (current_time - start_time).total_seconds() / 3600
                
                # Only restore tasks that haven't expired
                if elapsed_hours < keepalive_hours:
                    tasks[key] = {
                        'account_name': task['account_name'],
                        'cs_name': task['cs_name'],
                        'start_time': start_time,
                        'keepalive_hours': keepalive_hours
                    }
            
            return tasks
            
        except Exception as e:
            print(f"Error loading from GitHub: {e}")
            return {}
    
    @staticmethod
    def is_available() -> bool:
        """
        Check if GitHub storage is available
        
        Returns:
            True if token and repo are configured
        """
        try:
            import streamlit as st
            if hasattr(st, 'secrets') and 'github_storage' in st.secrets:
                token = st.secrets['github_storage'].get('token', '')
                repo = st.secrets['github_storage'].get('repo', '')
                return bool(token and repo)
        except Exception:
            pass
        return False

