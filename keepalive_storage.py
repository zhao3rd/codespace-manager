"""
Keepalive Tasks Persistent Storage Module
Supports both local file storage and GitHub-based cloud storage
Optimized for local-first approach with GitHub sync
All time handling uses Beijing Timezone (UTC+8)
"""
import json
import os
import threading
import time
from datetime import datetime
from typing import Dict, Optional, Callable
from timezone_utils import get_beijing_time, format_beijing_time, parse_datetime_to_beijing


class KeepaliveStorage:
    """Manage persistent storage of keepalive tasks"""

    STORAGE_FILE = "keepalive_tasks.json"
    LOCK_FILE = "keepalive_tasks.lock"
    _file_lock = threading.Lock()
    _github_sync_enabled = None  # Cache GitHub availability
    _startup_sync_completed = False  # Track if startup sync was done
    _sync_thread = None  # Singleton sync thread
    _sync_queue = []  # Queue for sync tasks
    _sync_lock = threading.Lock()  # Lock for sync queue
    
    @staticmethod
    def _acquire_file_lock(timeout: float = 10.0) -> bool:
        """
        Acquire file lock for thread-safe operations

        Args:
            timeout: Maximum time to wait for lock

        Returns:
            True if lock acquired successfully
        """
        acquired = KeepaliveStorage._file_lock.acquire(timeout=timeout)
        if acquired:
            # Also create a lock file for process-level safety
            try:
                with open(KeepaliveStorage.LOCK_FILE, 'w') as f:
                    f.write(f"{os.getpid()}\n{time.time()}\n")
            except Exception:
                pass  # Lock file is best-effort
        return acquired

    @staticmethod
    def _release_file_lock():
        """Release file lock"""
        try:
            if KeepaliveStorage._file_lock.locked():
                KeepaliveStorage._file_lock.release()
            # Remove lock file
            if os.path.exists(KeepaliveStorage.LOCK_FILE):
                os.remove(KeepaliveStorage.LOCK_FILE)
        except Exception:
            pass

    @staticmethod
    def _is_github_sync_enabled() -> bool:
        """
        Check if GitHub sync is enabled and cache the result

        Returns:
            True if GitHub sync is configured and available
        """
        if KeepaliveStorage._github_sync_enabled is not None:
            return KeepaliveStorage._github_sync_enabled

        try:
            from github_storage import GitHubStorage
            import streamlit as st

            if hasattr(st, 'secrets') and 'github_storage' in st.secrets:
                token = st.secrets['github_storage'].get('token', '')
                repo = st.secrets['github_storage'].get('repo', '')
                branch = st.secrets['github_storage'].get('branch', 'main')

                if token and repo:
                    KeepaliveStorage._github_sync_enabled = True
                    print(f"🔧 GitHub sync enabled: {repo}/{branch}")
                    return True
                else:
                    print(f"⚠️ GitHub storage config incomplete, using local-only")
                    KeepaliveStorage._github_sync_enabled = False
                    return False
            else:
                if hasattr(st, 'secrets'):
                    print(f"ℹ️ 'github_storage' not found in Streamlit secrets, using local-only")
                else:
                    print(f"ℹ️ Streamlit secrets not available, using local-only")
                KeepaliveStorage._github_sync_enabled = False
                return False
        except Exception as e:
            print(f"⚠️ Error checking GitHub storage: {type(e).__name__}: {e}")
            KeepaliveStorage._github_sync_enabled = False
            return False

    @staticmethod
    def _load_from_local() -> Dict:
        """
        Load tasks from local file (thread-safe)

        Returns:
            Dictionary of keepalive tasks
        """
        if not os.path.exists(KeepaliveStorage.STORAGE_FILE):
            return {}

        try:
            with KeepaliveStorage._file_lock:
                with open(KeepaliveStorage.STORAGE_FILE, 'r', encoding='utf-8') as f:
                    serializable_tasks = json.load(f)

                # Convert ISO format strings back to datetime objects
                tasks = {}
                current_time = get_beijing_time().replace(tzinfo=None)

                for key, task in serializable_tasks.items():
                    start_time = parse_datetime_to_beijing(task['start_time'], assume_beijing=True)
                    keepalive_hours = task['keepalive_hours']

                    # Only restore tasks that haven't expired
                    elapsed_hours = (current_time - start_time).total_seconds() / 3600
                    if elapsed_hours < keepalive_hours:
                        task_dict = {
                            'account_name': task['account_name'],
                            'cs_name': task['cs_name'],
                            'start_time': start_time,
                            'keepalive_hours': keepalive_hours,
                            'created_by': task.get('created_by', 'unknown'),
                            'created_at': parse_datetime_to_beijing(task['created_at'], assume_beijing=True) if 'created_at' in task else start_time
                        }
                        # Restore new fields if present
                        if 'last_used_at' in task:
                            task_dict['last_used_at'] = parse_datetime_to_beijing(task['last_used_at'], assume_beijing=True) if isinstance(task['last_used_at'], str) else task['last_used_at']
                        if 'next_check_time' in task:
                            task_dict['next_check_time'] = parse_datetime_to_beijing(task['next_check_time'], assume_beijing=True) if isinstance(task['next_check_time'], str) else task['next_check_time']
                        tasks[key] = task_dict

                return tasks
        except Exception as e:
            print(f"Error loading local keepalive tasks: {e}")
            return {}

    @staticmethod
    def _save_to_local(tasks: Dict) -> bool:
        """
        Save tasks to local file (thread-safe)

        Args:
            tasks: Dictionary of keepalive tasks

        Returns:
            True if successful
        """
        try:
            # Convert datetime objects to ISO format strings
            serializable_tasks = {}
            for key, task in tasks.items():
                serializable_tasks[key] = {
                    'account_name': task['account_name'],
                    'cs_name': task['cs_name'],
                    'start_time': task['start_time'].isoformat(),
                    'keepalive_hours': task['keepalive_hours'],
                    'created_by': task.get('created_by', 'unknown'),
                    'created_at': task['created_at'].isoformat() if hasattr(task['created_at'], 'isoformat') else task['created_at']
                }
                # Add new fields if present
                if 'last_used_at' in task:
                    serializable_tasks[key]['last_used_at'] = task['last_used_at'].isoformat() if hasattr(task['last_used_at'], 'isoformat') else task['last_used_at']
                if 'next_check_time' in task:
                    serializable_tasks[key]['next_check_time'] = task['next_check_time'].isoformat() if hasattr(task['next_check_time'], 'isoformat') else task['next_check_time']

            with KeepaliveStorage._file_lock:
                with open(KeepaliveStorage.STORAGE_FILE, 'w', encoding='utf-8') as f:
                    json.dump(serializable_tasks, f, indent=2)

            return True
        except Exception as e:
            print(f"Error saving local keepalive tasks: {e}")
            return False

    @staticmethod
    def _sync_to_github_async(tasks: Dict):
        """
        Asynchronously sync tasks to GitHub using singleton background thread

        Args:
            tasks: Dictionary of keepalive tasks to sync
        """
        if not KeepaliveStorage._is_github_sync_enabled():
            return

        # Add tasks to sync queue
        with KeepaliveStorage._sync_lock:
            KeepaliveStorage._sync_queue.append(tasks.copy())
            # Keep only latest 5 sync tasks to prevent queue buildup
            if len(KeepaliveStorage._sync_queue) > 5:
                KeepaliveStorage._sync_queue = KeepaliveStorage._sync_queue[-5:]

        # Start sync thread if not already running
        if KeepaliveStorage._sync_thread is None or not KeepaliveStorage._sync_thread.is_alive():
            KeepaliveStorage._sync_thread = threading.Thread(
                target=KeepaliveStorage._sync_worker,
                daemon=True,
                name="GitHubSyncWorker"
            )
            KeepaliveStorage._sync_thread.start()

    @staticmethod
    def _sync_worker():
        """
        Background worker that processes GitHub sync queue
        """
        while True:
            try:
                # Check if there are tasks to sync
                tasks_to_sync = None
                with KeepaliveStorage._sync_lock:
                    if KeepaliveStorage._sync_queue:
                        # Get the latest tasks from queue
                        tasks_to_sync = KeepaliveStorage._sync_queue.pop()

                if tasks_to_sync is not None:
                    # Perform the actual sync
                    try:
                        from github_storage import GitHubStorage
                        import streamlit as st

                        if hasattr(st, 'secrets') and 'github_storage' in st.secrets:
                            token = st.secrets['github_storage'].get('token', '')
                            repo = st.secrets['github_storage'].get('repo', '')
                            branch = st.secrets['github_storage'].get('branch', 'main')

                            github_storage = GitHubStorage(token, repo, branch)
                            success = github_storage.save_tasks(tasks_to_sync)

                            if success:
                                print(f"✅ Background sync to GitHub completed ({len(tasks_to_sync)} tasks)")
                            else:
                                print(f"⚠️ Background sync to GitHub failed")
                    except Exception as e:
                        print(f"⚠️ Background sync error: {type(e).__name__}: {e}")

                # Sleep for a reasonable interval
                import time
                time.sleep(30)  # Check queue every 30 seconds

            except Exception as e:
                print(f"⚠️ Sync worker error: {type(e).__name__}: {e}")
                import time
                time.sleep(60)  # Wait longer on error

    @staticmethod
    def _startup_sync_from_github() -> Dict:
        """
        Perform one-time startup sync from GitHub to local
        Only called on first application startup

        Returns:
            Dictionary of tasks loaded from GitHub (merged with local)
        """
        if KeepaliveStorage._startup_sync_completed:
            return KeepaliveStorage._load_from_local()

        if not KeepaliveStorage._is_github_sync_enabled():
            KeepaliveStorage._startup_sync_completed = True
            return KeepaliveStorage._load_from_local()

        try:
            print("🔄 Performing startup sync from GitHub...")
            from github_storage import GitHubStorage
            import streamlit as st

            if hasattr(st, 'secrets') and 'github_storage' in st.secrets:
                token = st.secrets['github_storage'].get('token', '')
                repo = st.secrets['github_storage'].get('repo', '')
                branch = st.secrets['github_storage'].get('branch', 'main')

                github_storage = GitHubStorage(token, repo, branch)
                github_tasks = github_storage.load_tasks()

                # Load local tasks
                local_tasks = KeepaliveStorage._load_from_local()

                # Merge tasks, prioritizing newer ones based on start_time
                merged_tasks = local_tasks.copy()
                for key, task in github_tasks.items():
                    if key not in merged_tasks or task['start_time'] > merged_tasks[key]['start_time']:
                        merged_tasks[key] = task

                # Save merged tasks to local
                KeepaliveStorage._save_to_local(merged_tasks)

                KeepaliveStorage._startup_sync_completed = True
                print(f"✅ Startup sync completed: {len(merged_tasks)} tasks")
                return merged_tasks

        except Exception as e:
            print(f"⚠️ Startup sync failed: {type(e).__name__}: {e}")

        # Fallback to local only
        KeepaliveStorage._startup_sync_completed = True
        return KeepaliveStorage._load_from_local()
    
    @staticmethod
    def save_tasks(tasks: Dict) -> bool:
        """
        Save keepalive tasks using local-first approach with GitHub sync

        Args:
            tasks: Dictionary of keepalive tasks

        Returns:
            True if local save successful (GitHub sync is async)
        """
        # Always save to local file first (fast, reliable)
        local_success = KeepaliveStorage._save_to_local(tasks)

        if local_success:
            # Trigger async GitHub sync if enabled
            KeepaliveStorage._sync_to_github_async(tasks)

        return local_success
    
    @staticmethod
    def load_tasks() -> Dict:
        """
        Load keepalive tasks using local-first approach with startup sync

        Returns:
            Dictionary of keepalive tasks
        """
        # Perform startup sync only on first call
        return KeepaliveStorage._startup_sync_from_github()
    
    @staticmethod
    def add_task(account_name: str, cs_name: str, start_time: datetime, keepalive_hours: float,
                 last_used_at: datetime = None, next_check_time: datetime = None, created_by: str = None) -> bool:
        """
        Add a new keepalive task using local-first approach

        Args:
            account_name: Account name
            cs_name: Codespace name
            start_time: Start time
            keepalive_hours: Keepalive duration in hours
            last_used_at: Last used time (defaults to start_time if not provided)
            next_check_time: Next check time (calculated if not provided)
            created_by: User who created this task

        Returns:
            True if successful
        """
        from config import Config
        from datetime import timedelta

        # Load from local (no GitHub sync on read)
        tasks = KeepaliveStorage._load_from_local()
        task_key = f"{account_name}_{cs_name}"

        # Use start_time if last_used_at not provided
        if not last_used_at:
            last_used_at = start_time

        # Calculate next_check_time if not provided
        if not next_check_time:
            buffer_seconds = Config.get_check_buffer_seconds()
            next_check_time = last_used_at + timedelta(seconds=buffer_seconds)

        tasks[task_key] = {
            'account_name': account_name,
            'cs_name': cs_name,
            'start_time': start_time,
            'keepalive_hours': keepalive_hours,
            'created_by': created_by or 'unknown',
            'created_at': get_beijing_time().replace(tzinfo=None),
            'last_used_at': last_used_at,
            'next_check_time': next_check_time
        }

        return KeepaliveStorage.save_tasks(tasks)
    
    @staticmethod
    def remove_task(account_name: str, cs_name: str) -> bool:
        """
        Remove a keepalive task using local-first approach

        Args:
            account_name: Account name
            cs_name: Codespace name

        Returns:
            True if successful
        """
        # Load from local (no GitHub sync on read)
        tasks = KeepaliveStorage._load_from_local()
        task_key = f"{account_name}_{cs_name}"

        if task_key in tasks:
            del tasks[task_key]
            return KeepaliveStorage.save_tasks(tasks)

        return True
    
    @staticmethod
    def clear_expired_tasks() -> int:
        """
        Clear all expired keepalive tasks using local-first approach

        Returns:
            Number of tasks cleared
        """
        # Load from local (no GitHub sync on read)
        tasks = KeepaliveStorage._load_from_local()
        original_count = len(tasks)
        current_time = get_beijing_time().replace(tzinfo=None)

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
        Get a specific keepalive task using local-first approach

        Args:
            account_name: Account name
            cs_name: Codespace name

        Returns:
            Task dictionary or None
        """
        # Load from local (no GitHub sync on read)
        tasks = KeepaliveStorage._load_from_local()
        task_key = f"{account_name}_{cs_name}"
        return tasks.get(task_key)

    @staticmethod
    def can_manage_task(task: Dict, current_user: str) -> bool:
        """
        Check if current user can manage the task

        Args:
            task: Task dictionary
            current_user: Current user identifier

        Returns:
            True if user can manage the task
        """
        if not task:
            return False

        # For now, allow all users to manage all tasks
        # This can be extended to implement proper permission management
        return True

    @staticmethod
    def get_all_active_tasks() -> Dict:
        """
        Get all active keepalive tasks using local-first approach (for backend service)

        Returns:
            Dictionary of all active tasks
        """
        return KeepaliveStorage._load_from_local()

    @staticmethod
    def get_task_by_key(task_key: str) -> Optional[Dict]:
        """
        Get task by task key using local-first approach

        Args:
            task_key: Task key (account_name_cs_name)

        Returns:
            Task dictionary or None
        """
        # Load from local (no GitHub sync on read)
        tasks = KeepaliveStorage._load_from_local()
        return tasks.get(task_key)

    @staticmethod
    def update_task_check_time(task_key: str, last_used_at: datetime, next_check_time: datetime) -> bool:
        """
        Update task check time information using local-first approach

        Args:
            task_key: Task key (account_name_cs_name)
            last_used_at: New last_used_at time
            next_check_time: New next_check_time

        Returns:
            True if successful
        """
        # Load from local (no GitHub sync on read)
        tasks = KeepaliveStorage._load_from_local()

        if task_key not in tasks:
            return False

        tasks[task_key]['last_used_at'] = last_used_at
        tasks[task_key]['next_check_time'] = next_check_time

        return KeepaliveStorage.save_tasks(tasks)

