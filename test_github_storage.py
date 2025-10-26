"""
Test GitHub Storage Configuration
Run this script to diagnose GitHub storage issues
"""
import streamlit as st
from github_storage import GitHubStorage
import requests


def test_github_storage():
    """Test GitHub storage configuration"""
    
    st.title("🔍 GitHub Storage Diagnostics")
    
    # Check if secrets are configured
    st.header("1️⃣ Secrets Configuration")
    
    if not hasattr(st, 'secrets'):
        st.error("❌ Streamlit secrets not available")
        return
    
    if 'github_storage' not in st.secrets:
        st.error("❌ 'github_storage' section not found in secrets")
        st.info("Please add the following to your Streamlit secrets:")
        st.code("""
[github_storage]
token = "ghp_your_token_here"
repo = "username/repository"
branch = "main"
        """)
        return
    
    st.success("✅ Secrets configured")
    
    # Get configuration
    token = st.secrets['github_storage'].get('token', '')
    repo = st.secrets['github_storage'].get('repo', '')
    branch = st.secrets['github_storage'].get('branch', 'main')
    
    # Display configuration (masked)
    st.header("2️⃣ Configuration Values")
    
    col1, col2 = st.columns(2)
    with col1:
        if token:
            st.success(f"✅ Token: {token[:10]}... (configured)")
        else:
            st.error("❌ Token: not configured")
    
    with col2:
        if repo:
            st.success(f"✅ Repo: {repo}")
        else:
            st.error("❌ Repo: not configured")
    
    st.info(f"ℹ️ Branch: {branch}")
    
    if not token or not repo:
        st.error("❌ Configuration incomplete")
        return
    
    # Test GitHub API connection
    st.header("3️⃣ GitHub API Connection")
    
    with st.spinner("Testing GitHub API..."):
        headers = {
            "Authorization": f"token {token}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28"
        }
        
        # Test 1: Check token validity
        try:
            response = requests.get("https://api.github.com/user", headers=headers)
            if response.status_code == 200:
                user_data = response.json()
                st.success(f"✅ Token valid - Authenticated as: {user_data.get('login', 'Unknown')}")
            else:
                st.error(f"❌ Token invalid - Status: {response.status_code}")
                st.code(response.text)
                return
        except Exception as e:
            st.error(f"❌ API connection error: {e}")
            return
        
        # Test 2: Check repository access
        try:
            response = requests.get(
                f"https://api.github.com/repos/{repo}",
                headers=headers
            )
            if response.status_code == 200:
                repo_data = response.json()
                st.success(f"✅ Repository accessible: {repo_data.get('full_name', 'Unknown')}")
                
                # Check permissions
                permissions = repo_data.get('permissions', {})
                if permissions.get('push', False):
                    st.success("✅ Write permission: YES")
                else:
                    st.error("❌ Write permission: NO - Token needs 'repo' scope")
                    return
            elif response.status_code == 404:
                st.error(f"❌ Repository not found: {repo}")
                st.info("Please check the repository name format: 'username/repository'")
                return
            else:
                st.error(f"❌ Repository access error - Status: {response.status_code}")
                st.code(response.text)
                return
        except Exception as e:
            st.error(f"❌ Repository check error: {e}")
            return
        
        # Test 3: Check branch
        try:
            response = requests.get(
                f"https://api.github.com/repos/{repo}/branches/{branch}",
                headers=headers
            )
            if response.status_code == 200:
                st.success(f"✅ Branch exists: {branch}")
            elif response.status_code == 404:
                st.error(f"❌ Branch not found: {branch}")
                st.info("Common branch names: 'main', 'master'")
                return
            else:
                st.warning(f"⚠️ Branch check returned: {response.status_code}")
        except Exception as e:
            st.warning(f"⚠️ Branch check error: {e}")
    
    # Test 4: Test file creation
    st.header("4️⃣ Test File Creation")
    
    if st.button("🧪 Test Create/Update File"):
        with st.spinner("Testing file creation..."):
            try:
                storage = GitHubStorage(token, repo, branch)
                
                # Create test data
                from datetime import datetime
                test_tasks = {
                    'test_task': {
                        'account_name': 'test_account',
                        'cs_name': 'test_codespace',
                        'start_time': datetime.now(),
                        'keepalive_hours': 1.0
                    }
                }
                
                # Try to save
                result = storage.save_tasks(test_tasks)
                
                if result:
                    st.success("✅ Successfully created/updated file!")
                    st.info(f"Check your repository: {repo}")
                    st.code(f"Location: codespace-manager/keepalive_tasks.json")
                else:
                    st.error("❌ Failed to create/update file")
                    st.info("Check Streamlit Cloud logs for detailed error messages")
            except Exception as e:
                st.error(f"❌ Test failed: {type(e).__name__}: {e}")
                import traceback
                st.code(traceback.format_exc())
    
    # Summary
    st.header("5️⃣ Summary")
    st.success("✅ All checks passed! GitHub storage should work correctly.")
    st.info("""
    If you're still having issues:
    1. Check Streamlit Cloud logs for detailed error messages
    2. Verify the token has 'repo' scope
    3. Make sure the repository name format is correct: 'username/repository'
    4. Try the test file creation above
    """)


if __name__ == "__main__":
    test_github_storage()

