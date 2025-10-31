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
    """Store keepalive tasks in GitHub repository with optimized API usage"""

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
        self.max_retries = 2  # Reduced retry attempts for faster failure
        self._last_known_sha = None  # Cache SHA to reduce API calls
    
    def _get_file_sha(self, force_refresh: bool = False) -> Optional[str]:
        """Get current file SHA for updates with caching"""
        # Use cached SHA if available and not forcing refresh
        if not force_refresh and self._last_known_sha:
            return self._last_known_sha

        url = f"{self.base_url}/repos/{self.repo}/contents/{self.file_path}"
        params = {"ref": self.branch}

        try:
            response = requests.get(url, headers=self.headers, params=params, timeout=10)
            if response.status_code == 200:
                sha = response.json().get("sha")
                self._last_known_sha = sha  # Cache the SHA
                return sha
            elif response.status_code == 404:
                # File doesn't exist, clear cache
                self._last_known_sha = None
                return None
            else:
                # Error occurred, clear cache to force refresh next time
                self._last_known_sha = None
                return None
        except Exception:
            self._last_known_sha = None
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
                    # Add new fields if present
                    if 'last_used_at' in task:
                        serializable_tasks[key]['last_used_at'] = task['last_used_at'].isoformat() if hasattr(task['last_used_at'], 'isoformat') else task['last_used_at']
                    if 'next_check_time' in task:
                        serializable_tasks[key]['next_check_time'] = task['next_check_time'].isoformat() if hasattr(task['next_check_time'], 'isoformat') else task['next_check_time']
                    if 'created_by' in task:
                        serializable_tasks[key]['created_by'] = task['created_by']
                    if 'created_at' in task:
                        serializable_tasks[key]['created_at'] = task['created_at'].isoformat() if hasattr(task['created_at'], 'isoformat') else task['created_at']
                
                # Get current file SHA (use cache on first attempt, force refresh on retry)
                sha = self._get_file_sha(force_refresh=(attempt > 0))
                
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
                response = requests.put(url, headers=self.headers, json=data, timeout=10)

                if response.status_code in [200, 201]:
                    # Update cached SHA on success
                    if response.status_code == 200:
                        self._last_known_sha = response.json().get("sha")
                    print(f"✅ GitHub storage: Successfully saved {task_count} tasks")
                    return True
                elif response.status_code == 409:
                    # Conflict: file was modified by someone else, retry
                    print(f"⚠️ GitHub storage: Conflict detected on attempt {attempt + 1}, retrying...")
                    # Force refresh SHA on next attempt
                    self._last_known_sha = None
                    # Brief delay before retry
                    import time
                    time.sleep(0.5)
                    continue
                else:
                    error_msg = f"GitHub API error {response.status_code}"
                    try:
                        error_detail = response.json()
                        if 'message' in error_detail:
                            error_msg += f": {error_detail['message']}"
                    except:
                        error_msg += f": {response.text[:200]}"

                    print(f"❌ GitHub storage: {error_msg}")
                    # Clear cache on error
                    self._last_known_sha = None
                    return False
                    
            except Exception as e:
                print(f"❌ GitHub storage: Error on attempt {attempt + 1}: {type(e).__name__}: {e}")
                # Clear cache on exception
                self._last_known_sha = None
                if attempt == self.max_retries - 1:
                    return False

        print(f"❌ GitHub storage: Failed to save after {self.max_retries} attempts")
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
                    task_dict = {
                        'account_name': task['account_name'],
                        'cs_name': task['cs_name'],
                        'start_time': start_time,
                        'keepalive_hours': keepalive_hours
                    }
                    # Restore new fields if present
                    if 'last_used_at' in task:
                        task_dict['last_used_at'] = datetime.fromisoformat(task['last_used_at']) if isinstance(task['last_used_at'], str) else task['last_used_at']
                    if 'next_check_time' in task:
                        task_dict['next_check_time'] = datetime.fromisoformat(task['next_check_time']) if isinstance(task['next_check_time'], str) else task['next_check_time']
                    if 'created_by' in task:
                        task_dict['created_by'] = task['created_by']
                    if 'created_at' in task:
                        task_dict['created_at'] = datetime.fromisoformat(task['created_at']) if isinstance(task['created_at'], str) else task['created_at']
                    tasks[key] = task_dict
            
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

