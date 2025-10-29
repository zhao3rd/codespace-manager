"""
GitHub Codespaces API Integration Module
"""
import requests
from typing import List, Dict, Optional
import time
import logging
import random

# Configure logger for this module
logger = logging.getLogger(__name__)


class GitHubCodespacesManager:
    """Manager for GitHub Codespaces operations"""
    
    def __init__(self, token: str):
        """
        Initialize GitHub Codespaces Manager
        
        Args:
            token: GitHub Personal Access Token with codespace permissions
        """
        self.token = token
        self.base_url = "https://api.github.com"
        self.headers = {
            "Authorization": f"token {token}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28"
        }
    
    def list_codespaces(self) -> List[Dict]:
        """
        List all codespaces for the authenticated user
        
        Returns:
            List of codespace information
        """
        url = f"{self.base_url}/user/codespaces"
        try:
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            data = response.json()
            return data.get("codespaces", [])
        except requests.exceptions.RequestException as e:
            if hasattr(e, 'response') and e.response is not None:
                status_code = e.response.status_code
                rate_limit_remaining = e.response.headers.get('X-RateLimit-Remaining', 'unknown')
                logger.error(f"GitHub API request failed - Method: GET, URL: {url}, "
                           f"Status Code: {status_code}, Rate Limit Remaining: {rate_limit_remaining}, "
                           f"Error: {type(e).__name__}: {str(e)}")
            else:
                logger.error(f"GitHub API request failed - Method: GET, URL: {url}, Error: {type(e).__name__}: {str(e)}")
            raise Exception(f"Failed to list codespaces: {str(e)}")
    
    def get_codespace(self, codespace_name: str) -> Dict:
        """
        Get details of a specific codespace
        
        Args:
            codespace_name: Name of the codespace
            
        Returns:
            Codespace information
        """
        url = f"{self.base_url}/user/codespaces/{codespace_name}"
        try:
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"GitHub API request failed - Method: GET, URL: {url}, Codespace: {codespace_name}, Error: {type(e).__name__}: {str(e)}")
            raise Exception(f"Failed to get codespace {codespace_name}: {str(e)}")
    
    def create_codespace(
        self,
        repository: str,
        ref: str = "main",
        machine: str = "basicLinux32gb",
        location: str = "WestUs2",
        idle_timeout_minutes: int = 30
    ) -> Dict:
        """
        Create a new codespace
        
        Args:
            repository: Repository full name (owner/repo)
            ref: Git ref (branch, tag, or commit)
            machine: Machine type
            location: Geographic location
            idle_timeout_minutes: Idle timeout in minutes
            
        Returns:
            Created codespace information
        """
        url = f"{self.base_url}/repos/{repository}/codespaces"
        payload = {
            "ref": ref,
            "machine": machine,
            "location": location,
            "idle_timeout_minutes": idle_timeout_minutes
        }
        try:
            response = requests.post(url, headers=self.headers, json=payload)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"GitHub API request failed - Method: POST, URL: {url}, Repository: {repository}, Ref: {ref}, Error: {type(e).__name__}: {str(e)}")
            raise Exception(f"Failed to create codespace: {str(e)}")
    
    def start_codespace(self, codespace_name: str) -> Dict:
        """
        Start a stopped codespace
        
        Args:
            codespace_name: Name of the codespace
            
        Returns:
            Started codespace information
        """
        url = f"{self.base_url}/user/codespaces/{codespace_name}/start"
        try:
            response = requests.post(url, headers=self.headers)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"GitHub API request failed - Method: POST, URL: {url}, Codespace: {codespace_name}, Error: {type(e).__name__}: {str(e)}")
            raise Exception(f"Failed to start codespace {codespace_name}: {str(e)}")
    
    def stop_codespace(self, codespace_name: str) -> Dict:
        """
        Stop a running codespace
        
        Args:
            codespace_name: Name of the codespace
            
        Returns:
            Stopped codespace information
        """
        url = f"{self.base_url}/user/codespaces/{codespace_name}/stop"
        try:
            response = requests.post(url, headers=self.headers)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"GitHub API request failed - Method: POST, URL: {url}, Codespace: {codespace_name}, Error: {type(e).__name__}: {str(e)}")
            raise Exception(f"Failed to stop codespace {codespace_name}: {str(e)}")
    
    def delete_codespace(self, codespace_name: str) -> bool:
        """
        Delete a codespace
        
        Args:
            codespace_name: Name of the codespace
            
        Returns:
            True if successful
        """
        url = f"{self.base_url}/user/codespaces/{codespace_name}"
        try:
            response = requests.delete(url, headers=self.headers)
            response.raise_for_status()
            return True
        except requests.exceptions.RequestException as e:
            logger.error(f"GitHub API request failed - Method: DELETE, URL: {url}, Codespace: {codespace_name}, Error: {type(e).__name__}: {str(e)}")
            raise Exception(f"Failed to delete codespace {codespace_name}: {str(e)}")
    
    def list_available_machines(self, repository: str, ref: str = "main") -> List[Dict]:
        """
        List available machine types for a repository
        
        Args:
            repository: Repository full name (owner/repo)
            ref: Git ref
            
        Returns:
            List of available machines
        """
        url = f"{self.base_url}/repos/{repository}/codespaces/machines"
        params = {"ref": ref}
        try:
            response = requests.get(url, headers=self.headers, params=params)
            response.raise_for_status()
            data = response.json()
            return data.get("machines", [])
        except requests.exceptions.RequestException as e:
            logger.error(f"GitHub API request failed - Method: GET, URL: {url}, Repository: {repository}, Ref: {ref}, Error: {type(e).__name__}: {str(e)}")
            raise Exception(f"Failed to list machines: {str(e)}")
    
    def get_user_info(self, max_retries: int = 2) -> Dict:
        """
        Get authenticated user information with retry logic for transient failures

        Args:
            max_retries: Maximum number of retry attempts for transient failures

        Returns:
            User information
        """
        url = f"{self.base_url}/user"

        for attempt in range(max_retries + 1):
            try:
                response = requests.get(url, headers=self.headers)
                response.raise_for_status()
                return response.json()

            except requests.exceptions.RequestException as e:
                # Enhanced logging for user info endpoint debugging
                if hasattr(e, 'response') and e.response is not None:
                    status_code = e.response.status_code
                    response_headers = dict(e.response.headers)

                    # Log rate limit information if available
                    rate_limit_remaining = response_headers.get('X-RateLimit-Remaining', 'unknown')
                    rate_limit_reset = response_headers.get('X-RateLimit-Reset', 'unknown')

                    logger.error(f"GitHub API request failed - Attempt {attempt + 1}/{max_retries + 1}, "
                               f"Method: GET, URL: {url}, "
                               f"Status Code: {status_code}, "
                               f"Rate Limit Remaining: {rate_limit_remaining}, "
                               f"Rate Limit Reset: {rate_limit_reset}, "
                               f"Error: {type(e).__name__}: {str(e)}")

                    # Additional logging for 403 errors
                    if status_code == 403:
                        logger.warning(f"403 Forbidden detected - Possible causes: "
                                     f"1) Token lacks required permissions (need 'user' or 'read:user' scope), "
                                     f"2) Rate limit exceeded, "
                                     f"3) Token expired/revoked, "
                                     f"4) GitHub service issues")

                        # Retry on 403 errors (might be transient)
                        if attempt < max_retries:
                            wait_time = (2 ** attempt) + random.uniform(0, 1)  # Exponential backoff with jitter
                            logger.info(f"Retrying in {wait_time:.2f} seconds...")
                            time.sleep(wait_time)
                            continue

                else:
                    logger.error(f"GitHub API request failed - Attempt {attempt + 1}/{max_retries + 1}, "
                               f"Method: GET, URL: {url}, "
                               f"Error: {type(e).__name__}: {str(e)}")

                    # Retry on network errors
                    if attempt < max_retries:
                        wait_time = (2 ** attempt) + random.uniform(0, 1)
                        logger.info(f"Retrying in {wait_time:.2f} seconds...")
                        time.sleep(wait_time)
                        continue

                # If this is the last attempt, raise the exception
                if attempt == max_retries:
                    raise Exception(f"Failed to get user info after {max_retries + 1} attempts: {str(e)}")

        # This should not be reached, but just in case
        raise Exception(f"Failed to get user info: Unexpected error")

