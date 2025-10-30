"""
Configuration Module - Multi-Account Support
"""
import os
import json
from typing import Dict, List, Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class Config:
    """Configuration settings"""
    
    # Default codespace settings
    DEFAULT_MACHINE = "basicLinux32gb"
    DEFAULT_LOCATION = "WestUs2"
    DEFAULT_IDLE_TIMEOUT = 30
    DEFAULT_REF = "main"

    # Keepalive settings
    DEFAULT_KEEPALIVE_HOURS = 4.0
    DEFAULT_KEEPALIVE_CHECK_INTERVAL = 120  # seconds (2 minutes) - deprecated, kept for compatibility
    DEFAULT_CHECK_BUFFER_SECONDS = 1818  # 30 minutes 18 seconds
    
    # Machine type options
    MACHINE_TYPES = [
        "basicLinux32gb",
        "standardLinux32gb",
        "premiumLinux",
        "largePremiumLinux"
    ]
    
    # Location options
    LOCATIONS = [
        "EastUs",
        "WestUs2",
        "SouthEastAsia",
        "WestEurope"
    ]
    
    # Local accounts storage file
    ACCOUNTS_FILE = "accounts.json"
    
    @staticmethod
    def load_streamlit_secrets() -> Dict[str, str]:
        """
        Load accounts from Streamlit secrets
        
        Returns:
            Dictionary of account_name: token
        """
        try:
            import streamlit as st
            if hasattr(st, 'secrets') and 'accounts' in st.secrets:
                return dict(st.secrets['accounts'])
        except Exception:
            pass
        return {}
    
    @staticmethod
    def load_local_accounts() -> Dict[str, str]:
        """
        Load accounts from local JSON file
        
        Returns:
            Dictionary of account_name: token
        """
        if os.path.exists(Config.ACCOUNTS_FILE):
            try:
                with open(Config.ACCOUNTS_FILE, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception:
                pass
        return {}
    
    @staticmethod
    def save_local_accounts(accounts: Dict[str, str]) -> bool:
        """
        Save accounts to local JSON file
        
        Args:
            accounts: Dictionary of account_name: token
            
        Returns:
            True if successful
        """
        try:
            with open(Config.ACCOUNTS_FILE, 'w', encoding='utf-8') as f:
                json.dump(accounts, f, indent=2)
            return True
        except Exception:
            return False
    
    @staticmethod
    def get_all_accounts() -> Dict[str, str]:
        """
        Get all accounts from both Streamlit secrets and local file
        Streamlit secrets take priority over local accounts
        
        Returns:
            Dictionary of account_name: token
        """
        accounts = Config.load_local_accounts()
        streamlit_accounts = Config.load_streamlit_secrets()
        
        # Streamlit secrets override local accounts
        accounts.update(streamlit_accounts)
        
        return accounts
    
    @staticmethod
    def get_keepalive_check_interval() -> int:
        """
        Get keepalive check interval from environment or default

        Returns:
            Check interval in seconds
        """
        try:
            interval = os.getenv('KEEPALIVE_CHECK_INTERVAL')
            if interval:
                return int(interval)
        except (ValueError, TypeError):
            pass
        return Config.DEFAULT_KEEPALIVE_CHECK_INTERVAL

    @staticmethod
    def get_default_keepalive_hours() -> float:
        """
        Get default keepalive duration from environment or default

        Returns:
            Default keepalive duration in hours
        """
        try:
            hours = os.getenv('DEFAULT_KEEPALIVE_HOURS')
            if hours:
                return float(hours)
        except (ValueError, TypeError):
            pass
        return Config.DEFAULT_KEEPALIVE_HOURS

    @staticmethod
    def get_check_buffer_seconds() -> int:
        """
        Get check buffer time from Streamlit secrets, environment variable, or default
        
        Priority order:
        1. Streamlit secrets: keepalive.check_buffer_seconds
        2. Environment variable: KEEPALIVE_CHECK_BUFFER_SECONDS
        3. Default: DEFAULT_CHECK_BUFFER_SECONDS (1818)
        
        Returns:
            Buffer time in seconds
        """
        # Try Streamlit secrets first
        try:
            import streamlit as st
            if hasattr(st, 'secrets') and 'keepalive' in st.secrets:
                buffer = st.secrets['keepalive'].get('check_buffer_seconds')
                if buffer is not None:
                    return int(buffer)
        except Exception:
            pass
        
        # Try environment variable
        try:
            buffer = os.getenv('KEEPALIVE_CHECK_BUFFER_SECONDS')
            if buffer:
                return int(buffer)
        except (ValueError, TypeError):
            pass
        
        # Return default
        return Config.DEFAULT_CHECK_BUFFER_SECONDS
    
    @staticmethod
    def is_running_on_cloud() -> bool:
        """
        Check if running on Streamlit Cloud

        Returns:
            True if running on Streamlit Cloud
        """
        return os.getenv('STREAMLIT_SHARING_MODE') is not None or \
               os.getenv('STREAMLIT_SERVER_HEADLESS') == 'true'

