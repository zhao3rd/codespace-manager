"""
GitHub Codespaces Manager - Multi-Account Support
Streamlit Application for managing multiple GitHub accounts' codespaces
"""
import streamlit as st
from datetime import datetime
from github_api import GitHubCodespacesManager
from config import Config
from keepalive_storage import KeepaliveStorage
import time
from typing import Dict, Optional


# Page configuration
st.set_page_config(
    page_title="GitHub Codespaces Manager",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)


def init_session_state():
    """Initialize session state variables"""
    if "authenticated_user" not in st.session_state:
        st.session_state.authenticated_user = False
    if "accounts" not in st.session_state:
        st.session_state.accounts = {}
    if "current_account" not in st.session_state:
        st.session_state.current_account = None
    if "managers" not in st.session_state:
        st.session_state.managers = {}
    if "user_infos" not in st.session_state:
        st.session_state.user_infos = {}
    if "refresh_trigger" not in st.session_state:
        st.session_state.refresh_trigger = 0
    if "show_add_account" not in st.session_state:
        st.session_state.show_add_account = False
    if "keepalive_tasks" not in st.session_state:
        # Load keepalive tasks from persistent storage
        st.session_state.keepalive_tasks = KeepaliveStorage.load_tasks()
        # Clear expired tasks on startup
        cleared = KeepaliveStorage.clear_expired_tasks()
        if cleared > 0:
            st.session_state.keepalive_tasks = KeepaliveStorage.load_tasks()
    if "show_keepalive_dialog" not in st.session_state:
        st.session_state.show_keepalive_dialog = {}
    if "last_keepalive_check" not in st.session_state:
        st.session_state.last_keepalive_check = {}


def check_login_credentials(username: str, password: str) -> bool:
    """
    Check login credentials against Streamlit secrets
    
    Args:
        username: Username
        password: Password
        
    Returns:
        True if credentials are valid
    """
    try:
        import streamlit as st
        if hasattr(st, 'secrets') and 'login' in st.secrets:
            valid_username = st.secrets['login'].get('username', '')
            valid_password = st.secrets['login'].get('password', '')
            return username == valid_username and password == valid_password
    except Exception:
        pass
    
    # Fallback to default credentials if secrets not available
    return username == "admin" and password == "admin"


def display_login_page():
    """Display login page"""
    st.title("🔐 Login Required")
    st.markdown("---")
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("### Please login to continue")
        st.markdown("")
        
        with st.form("login_form"):
            username = st.text_input("Username", placeholder="Enter username")
            password = st.text_input("Password", type="password", placeholder="Enter password")
            
            submitted = st.form_submit_button("🔑 Login", use_container_width=True)
            
            if submitted:
                if check_login_credentials(username, password):
                    st.session_state.authenticated_user = True
                    st.session_state.accounts = Config.get_all_accounts()
                    st.success("✅ Login successful!")
                    time.sleep(0.5)
                    st.rerun()
                else:
                    st.error("❌ Invalid username or password")
        
        st.markdown("---")
        st.info("""
        **Configuration:**
        - Add login credentials in Streamlit secrets
        - Default: username=`admin`, password=`admin`
        """)


def get_manager(account_name: str) -> Optional[GitHubCodespacesManager]:
    """
    Get or create manager for an account
    
    Args:
        account_name: Account name
        
    Returns:
        GitHubCodespacesManager instance or None
    """
    if account_name not in st.session_state.managers:
        token = st.session_state.accounts.get(account_name)
        if not token:
            return None
        try:
            manager = GitHubCodespacesManager(token)
            user_info = manager.get_user_info()
            st.session_state.managers[account_name] = manager
            st.session_state.user_infos[account_name] = user_info
        except Exception as e:
            st.error(f"❌ Failed to initialize account {account_name}: {str(e)}")
            return None
    
    return st.session_state.managers.get(account_name)


def add_account(account_name: str, token: str) -> bool:
    """
    Add a new account
    
    Args:
        account_name: Account name
        token: GitHub token
        
    Returns:
        True if successful
    """
    try:
        # Test token validity
        manager = GitHubCodespacesManager(token)
        user_info = manager.get_user_info()
        
        # Add to session state
        st.session_state.accounts[account_name] = token
        st.session_state.managers[account_name] = manager
        st.session_state.user_infos[account_name] = user_info
        
        # Save to local file if not on cloud or if it's a user-added account
        if not Config.is_running_on_cloud():
            Config.save_local_accounts(st.session_state.accounts)
        else:
            # On cloud, save only user-added accounts (not from secrets)
            streamlit_accounts = Config.load_streamlit_secrets()
            local_accounts = {k: v for k, v in st.session_state.accounts.items() 
                            if k not in streamlit_accounts}
            Config.save_local_accounts(local_accounts)
        
        return True
    except Exception as e:
        st.error(f"❌ Failed to add account: {str(e)}")
        return False


def remove_account(account_name: str) -> bool:
    """
    Remove an account
    
    Args:
        account_name: Account name
        
    Returns:
        True if successful
    """
    try:
        # Check if from Streamlit secrets (cannot delete)
        streamlit_accounts = Config.load_streamlit_secrets()
        if account_name in streamlit_accounts:
            st.error("❌ Cannot delete accounts from Streamlit secrets")
            return False
        
        # Remove from session state
        if account_name in st.session_state.accounts:
            del st.session_state.accounts[account_name]
        if account_name in st.session_state.managers:
            del st.session_state.managers[account_name]
        if account_name in st.session_state.user_infos:
            del st.session_state.user_infos[account_name]
        
        # Update current account if needed
        if st.session_state.current_account == account_name:
            st.session_state.current_account = None
        
        # Save to local file
        Config.save_local_accounts(st.session_state.accounts)
        
        return True
    except Exception as e:
        st.error(f"❌ Failed to remove account: {str(e)}")
        return False


def format_datetime(dt_str):
    """Format datetime string"""
    if not dt_str:
        return "N/A"
    try:
        dt = datetime.fromisoformat(dt_str.replace('Z', '+00:00'))
        return dt.strftime('%Y-%m-%d %H:%M:%S')
    except:
        return dt_str


def get_status_emoji(state):
    """Get emoji for codespace state"""
    status_map = {
        "Available": "✅",
        "Starting": "🔄",
        "Stopped": "⏸️",
        "Shutdown": "🔴",
        "Unavailable": "❌",
        "Unknown": "❓"
    }
    return status_map.get(state, "❓")


def display_sidebar():
    """Display sidebar with account management"""
    with st.sidebar:
        st.title("🚀 Codespaces Manager")
        
        # Account selector
        st.header("👥 Accounts")
        
        accounts = st.session_state.accounts
        
        if accounts:
            account_names = list(accounts.keys())
            
            # Initialize managers for all accounts
            for acc_name in account_names:
                get_manager(acc_name)
            
            # Display account info
            for acc_name in account_names:
                col1, col2 = st.columns([3, 1])
                with col1:
                    user_info = st.session_state.user_infos.get(acc_name)
                    if user_info:
                        login = user_info.get('login', acc_name)
                        st.markdown(f"**{acc_name}** (@{login})")
                    else:
                        st.markdown(f"**{acc_name}**")
                
                with col2:
                    streamlit_accounts = Config.load_streamlit_secrets()
                    is_from_secrets = acc_name in streamlit_accounts
                    
                    if not is_from_secrets:
                        if st.button("🗑️", key=f"del_{acc_name}", help="Delete account"):
                            if remove_account(acc_name):
                                st.success(f"✅ Removed {acc_name}")
                                time.sleep(0.5)
                                st.rerun()
                    else:
                        st.markdown("🔒")  # Locked (from secrets)
            
            st.divider()
        
        # Add account button
        if st.button("➕ Add Account", use_container_width=True):
            st.session_state.show_add_account = True
        
        # Add account form
        if st.session_state.show_add_account:
            with st.form("add_account_form"):
                st.subheader("Add New Account")
                new_account_name = st.text_input("Account Name", placeholder="my-github-account")
                new_token = st.text_input("GitHub Token", type="password", placeholder="ghp_xxxx...")
                
                col1, col2 = st.columns(2)
                with col1:
                    if st.form_submit_button("✅ Add", use_container_width=True):
                        if new_account_name and new_token:
                            if add_account(new_account_name, new_token):
                                st.success(f"✅ Added {new_account_name}")
                                st.session_state.show_add_account = False
                                time.sleep(0.5)
                                st.rerun()
                        else:
                            st.error("❌ Please fill all fields")
                
                with col2:
                    if st.form_submit_button("❌ Cancel", use_container_width=True):
                        st.session_state.show_add_account = False
                        st.rerun()
        
        st.divider()
        
        # Refresh button
        if accounts:
            if st.button("🔄 Refresh All", use_container_width=True):
                st.session_state.refresh_trigger += 1
                st.rerun()
        
        # Environment info
        st.divider()
        st.header("ℹ️ Info")
        
        if Config.is_running_on_cloud():
            st.info("☁️ Running on Streamlit Cloud")
        else:
            st.info("💻 Running locally")
        
        st.caption(f"Total Accounts: **{len(accounts)}**")
        
        # Logout button
        st.divider()
        if st.button("🔓 Logout", use_container_width=True):
            st.session_state.authenticated_user = False
            st.session_state.accounts = {}
            st.session_state.managers = {}
            st.session_state.user_infos = {}
            st.rerun()
        
        # Help section
        st.divider()
        st.header("📖 Help")
        st.markdown("""
        **Multi-Account Support:**
        - Manage multiple GitHub accounts
        - Each account has its own token
        - Add/Remove accounts dynamically
        
        **Token Sources:**
        - 🔒 Streamlit Secrets (Cloud)
        - 💾 Local JSON file
        - ➕ Manually added
        
        **Storage Location:**
        - Local: `accounts.json`
        - Cloud: Streamlit Secrets
        - Auto-reload on restart
        """)


def check_and_maintain_keepalive(account_name: str, cs_name: str, manager: GitHubCodespacesManager):
    """
    Check and maintain keepalive for a codespace
    
    Args:
        account_name: Account name
        cs_name: Codespace name
        manager: GitHubCodespacesManager instance
    """
    task_key = f"{account_name}_{cs_name}"
    
    if task_key not in st.session_state.keepalive_tasks:
        return
    
    task = st.session_state.keepalive_tasks[task_key]
    start_time = task['start_time']
    keepalive_hours = task['keepalive_hours']
    
    # Calculate elapsed time
    elapsed_hours = (datetime.now() - start_time).total_seconds() / 3600
    
    # Check if keepalive period has expired
    if elapsed_hours >= keepalive_hours:
        # Remove from both session and storage
        st.session_state.keepalive_tasks.pop(task_key, None)
        KeepaliveStorage.remove_task(account_name, cs_name)
        return
    
    # Check codespace status
    try:
        cs = manager.get_codespace(cs_name)
        state = cs.get('state', 'Unknown')
        
        # If not running, try to restart
        if state in ["Stopped", "Shutdown"]:
            try:
                manager.start_codespace(cs_name)
                st.session_state.last_keepalive_check[task_key] = datetime.now()
            except Exception:
                pass
    except Exception:
        pass


def display_codespaces_for_account(account_name: str, manager: GitHubCodespacesManager):
    """
    Display codespaces for a specific account in table format
    
    Args:
        account_name: Account name
        manager: GitHubCodespacesManager instance
    """
    try:
        with st.spinner(f"Loading codespaces for {account_name}..."):
            codespaces = manager.list_codespaces()
        
        user_info = st.session_state.user_infos.get(account_name, {})
        login = user_info.get('login', account_name)
        
        st.subheader(f"👤 {account_name} (@{login})")
        
        if not codespaces:
            st.info("📭 No codespaces found for this account")
            return
        
        st.caption(f"Total: {len(codespaces)} codespace(s)")
        
        # Check keepalive tasks
        for cs in codespaces:
            cs_name = cs.get("name")
            check_and_maintain_keepalive(account_name, cs_name, manager)
        
        # Header row
        header_cols = st.columns([0.3, 2, 1, 1, 1, 1.5])
        with header_cols[0]:
            st.markdown("**Status**")
        with header_cols[1]:
            st.markdown("**Codespace / Repository**")
        with header_cols[2]:
            st.markdown("**Machine**")
        with header_cols[3]:
            st.markdown("**Location**")
        with header_cols[4]:
            st.markdown("**Last Used**")
        with header_cols[5]:
            st.markdown("**Actions**")
        
        st.markdown("---")
        
        # Display each codespace as a row
        for idx, cs in enumerate(codespaces):
            cs_name = cs.get("name")
            state = cs.get("state", "Unknown")
            emoji = get_status_emoji(state)
            repo = cs.get('repository', {}).get('full_name', 'N/A')
            branch = cs.get('git_status', {}).get('ref', 'N/A')
            machine = cs.get('machine', {}).get('display_name', 'N/A')
            location = cs.get('location', 'N/A')
            last_used = format_datetime(cs.get('last_used_at'))
            web_url = cs.get('web_url', '')
            
            # Check if keepalive is active
            task_key = f"{account_name}_{cs_name}"
            is_keepalive_active = task_key in st.session_state.keepalive_tasks
            keepalive_info = ""
            if is_keepalive_active:
                task = st.session_state.keepalive_tasks[task_key]
                elapsed = (datetime.now() - task['start_time']).total_seconds() / 3600
                remaining = task['keepalive_hours'] - elapsed
                keepalive_info = f" 🔄 ({remaining:.1f}h left)"
            
            # Data row
            cols = st.columns([0.3, 2, 1, 1, 1, 1.5])
            
            with cols[0]:
                st.markdown(f"{emoji}")
            
            with cols[1]:
                st.markdown(f"**{cs_name}**{keepalive_info}")
                st.caption(f"📦 {repo}")
                st.caption(f"🌿 {branch}")
                if web_url:
                    st.markdown(f"[🌐 Open]({web_url})")
            
            with cols[2]:
                st.markdown(machine)
            
            with cols[3]:
                st.markdown(location)
            
            with cols[4]:
                st.markdown(last_used)
            
            with cols[5]:
                # Action buttons in a row
                action_cols = st.columns(3)
                
                # Refresh button
                with action_cols[0]:
                    if st.button("🔄", key=f"refresh_{account_name}_{idx}", help="Refresh", use_container_width=True):
                        st.rerun()
                
                # Start/Stop button
                with action_cols[1]:
                    if state == "Available":
                        if st.button("⏸️", key=f"stop_{account_name}_{idx}", help="Stop", use_container_width=True):
                            with st.spinner("Stopping..."):
                                try:
                                    manager.stop_codespace(cs_name)
                                    # Remove keepalive task from both session and storage
                                    st.session_state.keepalive_tasks.pop(task_key, None)
                                    KeepaliveStorage.remove_task(account_name, cs_name)
                                    st.success(f"✅ Stopped")
                                    time.sleep(1)
                                    st.rerun()
                                except Exception as e:
                                    st.error(f"❌ Error: {str(e)}")
                    
                    elif state in ["Stopped", "Shutdown"]:
                        if st.button("▶️", key=f"start_{account_name}_{idx}", help="Start with keepalive", use_container_width=True):
                            st.session_state.show_keepalive_dialog[task_key] = True
                            st.rerun()
                
                # Keepalive toggle
                with action_cols[2]:
                    if is_keepalive_active:
                        if st.button("❌", key=f"stop_keepalive_{account_name}_{idx}", help="Stop keepalive", use_container_width=True):
                            # Remove from both session and storage
                            st.session_state.keepalive_tasks.pop(task_key, None)
                            KeepaliveStorage.remove_task(account_name, cs_name)
                            st.success("Keepalive stopped")
                            st.rerun()
            
            # Keepalive dialog
            if st.session_state.show_keepalive_dialog.get(task_key, False):
                with st.form(f"keepalive_form_{account_name}_{idx}"):
                    st.markdown(f"**Set Keepalive for {cs_name}**")
                    keepalive_hours = st.number_input(
                        "Keepalive Duration (hours)",
                        min_value=0.5,
                        max_value=24.0,
                        value=4.0,
                        step=0.5,
                        help="Codespace will be kept alive for this duration"
                    )
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        if st.form_submit_button("✅ Start", use_container_width=True):
                            with st.spinner("Starting with keepalive..."):
                                try:
                                    manager.start_codespace(cs_name)
                                    start_time = datetime.now()
                                    
                                    # Add keepalive task to session state
                                    st.session_state.keepalive_tasks[task_key] = {
                                        'start_time': start_time,
                                        'keepalive_hours': keepalive_hours,
                                        'account_name': account_name,
                                        'cs_name': cs_name
                                    }
                                    
                                    # Save to persistent storage
                                    KeepaliveStorage.add_task(
                                        account_name=account_name,
                                        cs_name=cs_name,
                                        start_time=start_time,
                                        keepalive_hours=keepalive_hours
                                    )
                                    
                                    st.session_state.show_keepalive_dialog[task_key] = False
                                    st.success(f"✅ Started with {keepalive_hours}h keepalive (saved)")
                                    time.sleep(1)
                                    st.rerun()
                                except Exception as e:
                                    st.error(f"❌ Error: {str(e)}")
                    
                    with col2:
                        if st.form_submit_button("❌ Cancel", use_container_width=True):
                            st.session_state.show_keepalive_dialog[task_key] = False
                            st.rerun()
            
            st.markdown("")  # Spacing
        
        st.markdown("---")
    
    except Exception as e:
        st.error(f"❌ Failed to load codespaces for {account_name}: {str(e)}")


def display_all_codespaces():
    """Display codespaces for all accounts"""
    accounts = st.session_state.accounts
    
    if not accounts:
        st.info("👈 Please add an account using the sidebar")
        return
    
    # Display keepalive status summary
    active_keepalives = len(st.session_state.keepalive_tasks)
    if active_keepalives > 0:
        st.info(f"🔄 {active_keepalives} active keepalive task(s). Page auto-refreshes every 10 minutes.")
        
        # Auto-refresh if there are active keepalive tasks
        if active_keepalives > 0:
            # Use a placeholder for auto-refresh countdown
            import time as time_module
            refresh_placeholder = st.empty()
            
            # Show countdown and refresh after 60 seconds
            st.markdown("---")
    
    st.header("📋 All Codespaces")
    
    for account_name in accounts.keys():
        manager = get_manager(account_name)
        if manager:
            display_codespaces_for_account(account_name, manager)
    
    # Auto-refresh mechanism for keepalive
    if active_keepalives > 0:
        st.markdown("---")
        col1, col2 = st.columns([3, 1])
        with col1:
            st.caption("🔄 Auto-refresh is enabled due to active keepalive tasks (every 10 minutes)")
        with col2:
            if st.button("🔄 Refresh Now", use_container_width=True):
                st.rerun()
        
        # JavaScript auto-refresh after 10 minutes (600 seconds)
        st.markdown(
            """
            <script>
                setTimeout(function() {
                    window.location.reload();
                }, 600000);
            </script>
            """,
            unsafe_allow_html=True
        )


def display_create_codespace():
    """Display create codespace form"""
    accounts = st.session_state.accounts
    
    if not accounts:
        st.warning("⚠️ Please add at least one account first")
        return
    
    st.header("➕ Create New Codespace")
    
    with st.form("create_codespace_form"):
        # Account selector
        account_name = st.selectbox(
            "Account",
            options=list(accounts.keys()),
            help="Select which account to create the codespace for"
        )
        
        col1, col2 = st.columns(2)
        
        with col1:
            repository = st.text_input(
                "Repository (owner/repo)",
                placeholder="octocat/Hello-World",
                help="Enter the full repository name in format: owner/repo"
            )
            
            ref = st.text_input(
                "Branch/Ref",
                value=Config.DEFAULT_REF,
                help="Git branch, tag, or commit SHA"
            )
            
            machine = st.selectbox(
                "Machine Type",
                options=Config.MACHINE_TYPES,
                index=0,
                help="Select the machine type for the codespace"
            )
        
        with col2:
            location = st.selectbox(
                "Location",
                options=Config.LOCATIONS,
                index=1,
                help="Geographic location for the codespace"
            )
            
            idle_timeout = st.number_input(
                "Idle Timeout (minutes)",
                min_value=5,
                max_value=240,
                value=Config.DEFAULT_IDLE_TIMEOUT,
                help="Minutes of inactivity before auto-shutdown"
            )
        
        submitted = st.form_submit_button("🚀 Create Codespace", use_container_width=True)
        
        if submitted:
            if not repository:
                st.error("❌ Please provide a repository name")
            else:
                manager = get_manager(account_name)
                if not manager:
                    st.error(f"❌ Failed to get manager for {account_name}")
                    return
                
                with st.spinner(f"Creating codespace for {repository} on {account_name}..."):
                    try:
                        result = manager.create_codespace(
                            repository=repository,
                            ref=ref,
                            machine=machine,
                            location=location,
                            idle_timeout_minutes=idle_timeout
                        )
                        st.success(f"✅ Codespace created: {result.get('name')}")
                        st.info("🔄 Refreshing list...")
                        time.sleep(2)
                        st.rerun()
                    except Exception as e:
                        st.error(f"❌ Failed to create codespace: {str(e)}")


def display_account_management():
    """Display account management interface"""
    st.header("👥 Account Management")
    
    accounts = st.session_state.accounts
    streamlit_accounts = Config.load_streamlit_secrets()
    
    if not accounts:
        st.info("No accounts configured. Add one using the sidebar!")
        return
    
    st.subheader(f"Total Accounts: {len(accounts)}")
    
    # Display accounts in a table
    account_data = []
    for acc_name, token in accounts.items():
        user_info = st.session_state.user_infos.get(acc_name, {})
        login = user_info.get('login', 'N/A')
        source = "🔒 Streamlit Secrets" if acc_name in streamlit_accounts else "💾 Local Storage"
        
        account_data.append({
            "Account Name": acc_name,
            "GitHub Login": login,
            "Source": source,
            "Token": f"{token[:10]}..." if token else "N/A"
        })
    
    if account_data:
        # Use st.table instead of st.dataframe to avoid pyarrow DLL issues on Windows
        st.table(account_data)
    
    st.divider()
    
    # Instructions
    st.subheader("💡 How to Configure Accounts")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        **Local Development:**
        1. Click "Add Account" in sidebar
        2. Enter account name and token
        3. Accounts saved to `accounts.json`
        """)
    
    with col2:
        st.markdown("""
        **Streamlit Cloud:**
        1. Go to App Settings → Secrets
        2. Add accounts in TOML format
        3. See example below
        """)
    
    with st.expander("📄 Streamlit Secrets Example"):
        st.code("""
[accounts]
account1 = "ghp_your_token_here_1"
account2 = "ghp_your_token_here_2"
work_account = "ghp_your_token_here_3"
        """, language="toml")


def main():
    """Main application"""
    init_session_state()
    
    # Check if user is authenticated
    if not st.session_state.authenticated_user:
        display_login_page()
        return
    
    display_sidebar()
    
    accounts = st.session_state.accounts
    
    if not accounts:
        # Welcome screen
        st.title("🚀 GitHub Codespaces Manager")
        st.markdown("""
        ### Welcome to Multi-Account Codespaces Manager!
        
        This application helps you manage GitHub Codespaces across **multiple accounts** from a single interface.
        
        **Features:**
        - 👥 **Multi-Account Support** - Manage codespaces from multiple GitHub accounts
        - 📋 View all codespaces at a glance
        - ▶️ Start and ⏸️ stop codespaces
        - ❌ Delete unused codespaces
        - ➕ Create new codespaces
        - 🔄 Real-time status updates
        - ☁️ Works on local and Streamlit Cloud
        
        **To get started:**
        1. Click "**Add Account**" in the sidebar
        2. Enter your account name and GitHub token
        3. Start managing your codespaces!
        
        ---
        """)
        
        st.info("👈 Please add an account using the sidebar to continue")
    else:
        # Main dashboard
        st.title("🚀 GitHub Codespaces Manager")
        st.markdown(f"Managing **{len(accounts)}** GitHub account(s) 👥")
        st.markdown("---")
        
        # Tabs for different sections
        tab1, tab2, tab3 = st.tabs(["📋 All Codespaces", "➕ Create New", "👥 Account Management"])
        
        with tab1:
            display_all_codespaces()
        
        with tab2:
            display_create_codespace()
        
        with tab3:
            display_account_management()


if __name__ == "__main__":
    main()
