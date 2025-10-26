"""
GitHub Codespaces API Integration Module
"""
import requests
from typing import List, Dict, Optional
import time


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
            raise Exception(f"Failed to list machines: {str(e)}")
    
    def get_user_info(self) -> Dict:
        """
        Get authenticated user information
        
        Returns:
            User information
        """
        url = f"{self.base_url}/user"
        try:
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            raise Exception(f"Failed to get user info: {str(e)}")

