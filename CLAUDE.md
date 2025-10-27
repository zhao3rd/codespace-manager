# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a GitHub Codespaces Manager built with Streamlit that supports managing multiple GitHub accounts from a single interface. It provides a web-based dashboard for viewing, starting, stopping, and creating codespaces across different GitHub accounts.

## Core Architecture

### Main Components

**streamlit_app.py** - Main Streamlit application with authentication, multi-account management, and UI components
- Handles user authentication via Streamlit secrets
- Manages session state for accounts, managers, and keepalive tasks
- Provides tabbed interface for viewing codespaces, creating new ones, and account management
- Implements auto-refresh for keepalive functionality

**github_api.py** - GitHub API integration module wrapping the Codespaces API
- `GitHubCodespacesManager` class handles all GitHub API operations
- Methods: list_codespaces(), get_codespace(), create_codespace(), start_codespace(), stop_codespace()
- Uses GitHub API v2022-11-28 with proper authentication headers

**config.py** - Configuration management supporting both local and cloud deployment
- Handles loading accounts from Streamlit secrets and local JSON files
- Provides default codespace settings (machine types, locations, timeouts)
- Detects running environment (local vs Streamlit Cloud)

**keepalive_storage.py** - Persistent storage abstraction layer for keepalive tasks
- Supports both local file storage and GitHub-based cloud storage
- Automatically chooses backend based on available configuration
- Handles task persistence across application restarts

**github_storage.py** - GitHub API-based storage backend for keepalive tasks
- Stores keepalive tasks as JSON in a GitHub repository file
- Implements conflict resolution and retry logic for concurrent access
- Enables persistence on Streamlit Cloud where local filesystem isn't reliable

## Common Development Commands

### Running the Application
```bash
# Install dependencies
pip install -r requirements.txt

# Run locally (requires .streamlit/secrets.toml configuration)
streamlit run streamlit_app.py
```

### Testing
```bash
# Test GitHub storage functionality
python test_github_storage.py
```

## Configuration

### Local Development Setup
1. Create `.streamlit/secrets.toml` for login credentials:
```toml
[login]
username = "admin"
password = "your_password"
```

2. Create `accounts.json` for GitHub accounts:
```json
{
  "personal_account": "ghp_your_token_here",
  "work_account": "ghp_work_token_here"
}
```

### Streamlit Cloud Configuration
Configure in App Settings → Secrets:
```toml
[login]
username = "admin"
password = "your_password"

[accounts]
account1 = "ghp_token1"
account2 = "ghp_token2"

[github_storage]
token = "ghp_storage_token"
repo = "your-username/codespace-manager"
branch = "main"
```

## Key Features

### Multi-Account Support
- Each account has its own GitHub token and manager instance
- Accounts can be added/removed dynamically through the UI
- Streamlit secrets accounts are locked (🔒) and cannot be deleted in-app

### Keepalive System
- Automatic codespace monitoring and restart functionality
- Persistent storage of keepalive tasks (local file or GitHub repository)
- Configurable duration (0.5-24 hours)
- Auto-refresh page every 10 minutes when keepalive tasks are active

### Storage Architecture
- **Local**: `accounts.json` for accounts, `keepalive_tasks.json` for tasks
- **Cloud**: Streamlit secrets for accounts, GitHub repository for tasks
- Automatic backend selection based on deployment environment

## Security Considerations

- GitHub tokens require only `codespace` permission
- Tokens are never displayed in plain text (password fields)
- Sensitive files are in `.gitignore` (`accounts.json`, `keepalive_tasks.json`)
- Authentication required before accessing any functionality

## Error Handling

The application includes comprehensive error handling for:
- Invalid GitHub tokens or expired credentials
- Network connectivity issues
- API rate limiting
- Storage backend failures
- Concurrent access conflicts for GitHub storage

## Session State Management

Key session variables:
- `authenticated_user` - Login status
- `accounts` - Dictionary of account_name: token
- `managers` - GitHubCodespacesManager instances per account
- `user_infos` - Cached GitHub user information
- `keepalive_tasks` - Active keepalive tasks loaded from persistent storage
- `refresh_trigger` - Incremental trigger for UI refreshes