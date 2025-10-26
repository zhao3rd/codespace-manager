"""
Keepalive Tasks Persistent Storage Module
Supports both local file storage and GitHub-based cloud storage
"""
import json
import os
from datetime import datetime
from typing import Dict, Optional


class KeepaliveStorage:
    """Manage persistent storage of keepalive tasks"""
    
    STORAGE_FILE = "keepalive_tasks.json"
    
    @staticmethod
    def _get_storage_backend():
        """
        Get the appropriate storage backend
        
        Returns:
            Storage backend instance (GitHub or local file)
        """
        try:
            # Try to use GitHub storage if available
            from github_storage import GitHubStorage
            import streamlit as st
            
            if hasattr(st, 'secrets') and 'github_storage' in st.secrets:
                token = st.secrets['github_storage'].get('token', '')
                repo = st.secrets['github_storage'].get('repo', '')
                branch = st.secrets['github_storage'].get('branch', 'main')
                
                if token and repo:
                    return GitHubStorage(token, repo, branch)
        except Exception:
            pass
        
        # Fallback to local file storage
        return None
    
    @staticmethod
    def save_tasks(tasks: Dict) -> bool:
        """
        Save keepalive tasks to storage (GitHub or local file)
        
        Args:
            tasks: Dictionary of keepalive tasks
            
        Returns:
            True if successful
        """
        # Try GitHub storage first
        github_storage = KeepaliveStorage._get_storage_backend()
        if github_storage:
            return github_storage.save_tasks(tasks)
        
        # Fallback to local file storage
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
            
            with open(KeepaliveStorage.STORAGE_FILE, 'w', encoding='utf-8') as f:
                json.dump(serializable_tasks, f, indent=2)
            
            return True
        except Exception as e:
            print(f"Error saving keepalive tasks: {e}")
            return False
    
    @staticmethod
    def load_tasks() -> Dict:
        """
        Load keepalive tasks from storage (GitHub or local file)
        
        Returns:
            Dictionary of keepalive tasks
        """
        # Try GitHub storage first
        github_storage = KeepaliveStorage._get_storage_backend()
        if github_storage:
            return github_storage.load_tasks()
        
        # Fallback to local file storage
        if not os.path.exists(KeepaliveStorage.STORAGE_FILE):
            return {}
        
        try:
            with open(KeepaliveStorage.STORAGE_FILE, 'r', encoding='utf-8') as f:
                serializable_tasks = json.load(f)
            
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
            print(f"Error loading keepalive tasks: {e}")
            return {}
    
    @staticmethod
    def add_task(account_name: str, cs_name: str, start_time: datetime, keepalive_hours: float) -> bool:
        """
        Add a new keepalive task
        
        Args:
            account_name: Account name
            cs_name: Codespace name
            start_time: Start time
            keepalive_hours: Keepalive duration in hours
            
        Returns:
            True if successful
        """
        tasks = KeepaliveStorage.load_tasks()
        task_key = f"{account_name}_{cs_name}"
        
        tasks[task_key] = {
            'account_name': account_name,
            'cs_name': cs_name,
            'start_time': start_time,
            'keepalive_hours': keepalive_hours
        }
        
        return KeepaliveStorage.save_tasks(tasks)
    
    @staticmethod
    def remove_task(account_name: str, cs_name: str) -> bool:
        """
        Remove a keepalive task
        
        Args:
            account_name: Account name
            cs_name: Codespace name
            
        Returns:
            True if successful
        """
        tasks = KeepaliveStorage.load_tasks()
        task_key = f"{account_name}_{cs_name}"
        
        if task_key in tasks:
            del tasks[task_key]
            return KeepaliveStorage.save_tasks(tasks)
        
        return True
    
    @staticmethod
    def clear_expired_tasks() -> int:
        """
        Clear all expired keepalive tasks
        
        Returns:
            Number of tasks cleared
        """
        tasks = KeepaliveStorage.load_tasks()
        original_count = len(tasks)
        current_time = datetime.now()
        
        # Filter out expired tasks
        active_tasks = {}
        for key, task in tasks.items():
            elapsed_hours = (current_time - task['start_time']).total_seconds() / 3600
            if elapsed_hours < task['keepalive_hours']:
                active_tasks[key] = task
        
        if len(active_tasks) < original_count:
            KeepaliveStorage.save_tasks(active_tasks)
        
        return original_count - len(active_tasks)
    
    @staticmethod
    def get_task(account_name: str, cs_name: str) -> Optional[Dict]:
        """
        Get a specific keepalive task
        
        Args:
            account_name: Account name
            cs_name: Codespace name
            
        Returns:
            Task dictionary or None
        """
        tasks = KeepaliveStorage.load_tasks()
        task_key = f"{account_name}_{cs_name}"
        return tasks.get(task_key)

