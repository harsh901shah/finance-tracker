"""
Main entry point for the Finance Tracker application.

This module initializes and runs the Finance Tracker application, handling
authentication, page navigation, and overall application flow.

NOTE: All Streamlit session keys for Finance Tracker are now prefixed with 'ft_' 
for clarity and isolation (e.g., ft_user, ft_authenticated, ft_current_page).
"""

import streamlit as st
import os
import traceback
import logging
from pages.dashboard_page import DashboardPage
from pages.networth_page import NetWorthPage
from pages.transaction_page import TransactionPage
from pages.add_transaction_page import AddTransactionPage
from pages.add_transaction_page_v2 import AddTransactionPageV2
from pages.template_manager_page import TemplateManagerPage
from pages.budget_page import BudgetPage
from pages.login_page import LoginPage
from services.database_service import DatabaseService
from services.auth_service import AuthService
from services.logger_service import LoggerService
from components.onboarding import OnboardingGuide
from components.user_profile import UserProfile
from utils.auth_middleware import AuthMiddleware
from services.onboarding_service import OnboardingService
from services.tooltip_service import TooltipService
import time

# Set page configuration
st.set_page_config(
    page_title="Personal Finance Tracker",
    page_icon="💰",
    layout="wide"
)

class FinanceApp:
    """
    Main Finance Tracker Application class.
    
    This class initializes the application, manages database connections,
    handles authentication, and controls page navigation and rendering.
    """
    
    logger = LoggerService.get_logger('finance_app')
    
    def __init__(self):
        """
        Initialize the Finance Tracker application.
        
        Sets up the database, configures logging, and initializes
        the page navigation dictionary.
        """
        self.logger.info("Initializing Finance Tracker Application")
        
        # Initialize database
        self._initialize_database()
        
        # Dictionary of available pages with their handler classes/methods
        self.pages = {
            "Dashboard": DashboardPage,
            "Net Worth": NetWorthPage,
            "View Transactions": TransactionPage.show_list,
            "Add Transaction": AddTransactionPageV2,
            "Manage Templates": TemplateManagerPage,
            "Budget": BudgetPage
        }
    
    def _initialize_database(self):
        """
        Initialize the application database.
        
        Creates necessary database tables and ensures the database
        is properly configured for the application.
        """
        try:
            # Create database tables
            DatabaseService.initialize_database()
            self.logger.info("Database initialized successfully")
        except IOError as e:
            # Handle database file/permission errors
            error_msg = f"Database setup failed: {str(e)}"
            self.logger.error(error_msg)
            st.error("🗄️ Database Setup Error")
            st.error(error_msg)
            st.info("💡 **Solutions:**\n- Check file permissions\n- Ensure sufficient disk space\n- Restart the application")
        except ConnectionError as e:
            # Handle database connection errors
            error_msg = f"Database connection failed: {str(e)}"
            self.logger.error(error_msg)
            st.error("🔌 Database Connection Error")
            st.error(error_msg)
            st.info("💡 **Solutions:**\n- Check if database file is locked\n- Restart the application")
        except RuntimeError as e:
            # Handle database runtime errors
            error_msg = f"Database runtime error: {str(e)}"
            self.logger.error(error_msg)
            st.error("⚠️ Database Runtime Error")
            st.error(error_msg)
            st.info("💡 **Solutions:**\n- Delete the database file to reset\n- Contact support if issue persists")
        except Exception as e:
            # Handle any other unexpected errors
            error_msg = f"Unexpected database error: {str(e)}"
            self.logger.error(f"{error_msg}\n{traceback.format_exc()}")
            st.error("🚨 Unexpected Database Error")
            st.error(error_msg)
            st.info("💡 **Solutions:**\n- Restart the application\n- Check the logs for details\n- Contact support")

    
    def run(self):
        """
        Run the Finance Tracker application.
        
        Handles authentication flow, page navigation, and renders
        the appropriate page based on user selection.
        """
        try:
            self.logger.info("Starting Finance Tracker application")
            
            # Initialize session state for authentication with prefixed keys
            if "ft_authenticated" not in st.session_state:
                st.session_state.ft_authenticated = False
            if "ft_user" not in st.session_state:
                st.session_state.ft_user = None
                
            # Check authentication status
            is_authenticated = LoginPage.verify_authentication()
            
            if not is_authenticated:
                # Show login page if not authenticated - NO SIDEBAR
                is_authenticated = LoginPage.show()
                
            if is_authenticated:
                # User is authenticated, show the main app with sidebar
                
                # Get current user for all operations
                current_user = AuthMiddleware.get_current_user_id()
                user_id = str(current_user.get('user_id') if isinstance(current_user, dict) else current_user or 'default_user')
                
                # Apply custom CSS for sidebar
                self._apply_sidebar_css()
                
                # Sidebar for navigation - ONLY when authenticated
                with st.sidebar:
                    # Get personalized display name
                    display_name = UserProfile.get_user_display_name()
                    st.markdown(f'<div class="sidebar-header"><h1>💰 Finance Tracker</h1><p>Welcome, {display_name}</p></div>', unsafe_allow_html=True)
                    
                    # Get current page or default to Dashboard
                    if "ft_current_page" not in st.session_state:
                        st.session_state.ft_current_page = "Dashboard"
                    
                    current_page = st.session_state.ft_current_page
                    selected_page = None
                    
                    # Overview section - Main dashboard and financial summary pages
                    st.markdown('<div class="nav-section"><div class="nav-label">OVERVIEW</div></div>', unsafe_allow_html=True)
                    if st.sidebar.button("Dashboard", key="nav_Dashboard", width="stretch", type="primary" if current_page == "Dashboard" else "secondary"):
                        selected_page = "Dashboard"
                        st.session_state.ft_current_page = "Dashboard"
                        st.rerun()  # Force page refresh to update active button styling
                    if st.sidebar.button("Net Worth", key="nav_Net_Worth", width="stretch", type="primary" if current_page == "Net Worth" else "secondary"):
                        selected_page = "Net Worth"
                        st.session_state.ft_current_page = "Net Worth"
                        st.rerun()
                    
                    # Transactions section - Core transaction management functionality
                    st.markdown('<div class="nav-section"><div class="nav-label">TRANSACTIONS</div></div>', unsafe_allow_html=True)
                    if st.sidebar.button("View Transactions", key="nav_View_Transactions", width="stretch", type="primary" if current_page == "View Transactions" else "secondary"):
                        selected_page = "View Transactions"
                        st.session_state.ft_current_page = "View Transactions"
                        st.rerun()
                    if st.sidebar.button("Add Transaction", key="nav_Add_Transaction", width="stretch", type="primary" if current_page == "Add Transaction" else "secondary"):
                        selected_page = "Add Transaction"
                        st.session_state.ft_current_page = "Add Transaction"
                        st.rerun()
                    if st.sidebar.button("Manage Templates", key="nav_Manage_Templates", width="stretch", type="primary" if current_page == "Manage Templates" else "secondary"):
                        selected_page = "Manage Templates"
                        st.session_state.ft_current_page = "Manage Templates"
                        st.rerun()
                    if st.sidebar.button("Budget", key="nav_Budget", width="stretch", type="primary" if current_page == "Budget" else "secondary"):
                        selected_page = "Budget"
                        st.session_state.ft_current_page = "Budget"
                        st.rerun()
                    

                    
                    # Use current page for display
                    selected_page = current_page
                    
                    # Show contextual tips
                    if OnboardingService.should_show_onboarding(user_id):
                        tips = OnboardingService.get_contextual_tips(current_page.lower().replace(' ', '_'), OnboardingService.get_user_progress(user_id))
                        if tips:
                            with st.expander("💡 Tips", expanded=False):
                                for tip in tips[:2]:  # Show max 2 tips
                                    st.info(tip)
                    
                    # End of navigation
                    
                    # Settings section
                    st.markdown('<div class="nav-section"><div class="nav-label">SETTINGS</div></div>', unsafe_allow_html=True)
                    
                    # Debug mode toggle
                    debug_mode = st.sidebar.checkbox("🔧 Debug Mode", value=st.session_state.get('ft_debug_mode', False), help="Show performance metrics and technical details")
                    st.session_state.ft_debug_mode = debug_mode
                    
                    # Logout button
                    st.markdown('<div class="logout-section"></div>', unsafe_allow_html=True)
                    if st.sidebar.button("Logout", key="logout_button", width="stretch", type="secondary"):
                        # Clear all cached data on logout
                        try:
                            from services.financial_data_service import TransactionService
                            TransactionService.clear_cache(user_id)
                        except Exception as cache_error:
                            self.logger.warning(f"Failed to clear cache on logout: {str(cache_error)}")
                        
                        if "ft_user" in st.session_state and st.session_state.ft_user and "session_token" in st.session_state.ft_user:
                            AuthService.logout(st.session_state.ft_user["session_token"])
                        
                        # Clear all application data except safe UI preferences (theme, language, ui_preferences) on logout
                        safe_keys = {'theme', 'language', 'ui_preferences'}
                        keys_to_remove = [key for key in st.session_state.keys() 
                                        if not key.startswith('st.') and key not in safe_keys]
                        for key in keys_to_remove:
                            del st.session_state[key]
                        
                        st.rerun()
            
                # Show onboarding checklist for new users
                if OnboardingService.should_show_onboarding(user_id):
                    with st.expander("🚀 Getting Started", expanded=True):
                        OnboardingService.show_onboarding_checklist(user_id)
                
                # Show contextual onboarding based on current page
                OnboardingService.show_onboarding_flow(user_id, selected_page.lower().replace(' ', '_'))
                
                # Display the selected page with security check
                try:
                    # Ensure user is still authenticated before showing pages
                    if not AuthMiddleware.is_authenticated():
                        st.error("🔒 Session expired. Please login again.")
                        st.session_state.ft_authenticated = False
                        st.rerun()
                        return
                    
                    page = selected_page
                    
                    # Performance monitoring
                    start_time = time.time()
                    
                    # Show contextual tooltip for current page
                    OnboardingGuide.show_page_tooltip(page)
                    
                    # Show feature highlights for new features
                    if page == "View Transactions":
                        with st.expander("✨ New Features", expanded=False):
                            OnboardingService.show_feature_highlights(['bulk_actions', 'undo_support', 'audit_log'])
                    
                    # Render the page with error boundary
                    try:
                        if page == "Add Transaction":
                            self.pages[page].show()
                            # Check for onboarding triggers
                            OnboardingService.check_onboarding_triggers(user_id, 'page_visited', {'page': 'add_transaction'})
                        elif page == "View Transactions":
                            self.pages[page]()
                        elif page == "Net Worth":
                            self.pages[page].show()
                            OnboardingService.check_onboarding_triggers(user_id, 'net_worth_viewed')
                        elif page == "Budget":
                            self.pages[page].show()
                            OnboardingService.check_onboarding_triggers(user_id, 'budget_viewed')
                        else:
                            self.pages[page].show()
                        
                        # Performance monitoring
                        load_time = time.time() - start_time
                        if load_time > 2.0:  # Log slow page loads
                            self.logger.warning(f"Slow page load: {page} took {load_time:.2f}s")
                        
                        # Show performance info in debug mode
                        if st.session_state.get('ft_debug_mode', False):
                            st.success(f"⚡ Page loaded in {load_time:.2f}s | 🔧 Debug Mode Active")
                    
                    except ImportError as page_error:
                        # Handle missing page modules
                        self.logger.error(f"Page module not found: {page} - {str(page_error)}")
                        st.error(f"🚫 Page '{page}' is not available")
                        st.info("💡 This feature may be under development. Try another page.")
                        if st.button("🏠 Go to Dashboard"):
                            st.session_state.current_page = "Dashboard"
                            st.rerun()
                    except AttributeError as page_error:
                        # Handle missing page methods
                        self.logger.error(f"Page method not found: {page} - {str(page_error)}")
                        st.error(f"⚠️ Page '{page}' has configuration issues")
                        st.info("💡 Please try refreshing or contact support.")
                        if st.button("🔄 Refresh Page"):
                            st.rerun()
                    except Exception as page_error:
                        # General page errors
                        self.logger.error(f"Error in page {page}: {str(page_error)}")
                        st.error(f"🚨 Error loading {page}")
                        st.error(str(page_error))
                        
                        # Show fallback content
                        st.info("💡 **Try these solutions:**")
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            if st.button("🏠 Dashboard"):
                                st.session_state.ft_current_page = "Dashboard"
                                st.rerun()
                        with col2:
                            if st.button("🔄 Refresh"):
                                st.rerun()
                        with col3:
                            if st.button("📞 Support"):
                                st.info("📧 support@financetracker.com")
                except Exception as e:
                    # Handle critical page display errors
                    error_msg = f"Critical error displaying page: {str(e)}"
                    self.logger.critical(f"{error_msg}\n{traceback.format_exc()}")
                    st.error("🚨 Critical Application Error")
                    st.error(error_msg)
                    st.info("💡 **Recovery Options:**\n- Refresh the page\n- Try a different section\n- Restart the application")
                    
                    # Only show detailed error/debug info in debug mode to avoid confusing end users
                    if st.session_state.get('ft_debug_mode', False):
                        with st.expander("🔧 Debug Information"):
                            st.code(f"Error: {str(e)}")
                            st.code(f"Traceback:\n{traceback.format_exc()}")
        except Exception as e:
            # Handle catastrophic application errors
            error_msg = f"Catastrophic application error: {str(e)}"
            self.logger.critical(f"{error_msg}\n{traceback.format_exc()}")
            st.error("💥 Application Crashed")
            st.error("The application encountered a critical error and cannot continue.")
            st.info("💡 **Recovery Steps:**\n1. Refresh your browser\n2. Restart the application\n3. Check the logs\n4. Contact support if issue persists")
            
            # Always show basic error info, detailed info only in debug mode
            st.code(f"Error Type: {type(e).__name__}")
            st.code(f"Error Message: {str(e)}")
            
            # Only show detailed error/debug info in debug mode to avoid confusing end users
            if st.session_state.get('ft_debug_mode', False):
                with st.expander("🔧 Full Debug Information"):
                    st.code(f"Full Traceback:\n{traceback.format_exc()}")
    
    @staticmethod
    def _apply_sidebar_css():
        """Apply custom CSS for professional sidebar styling.
        
        Creates enterprise-grade navigation with:
        - Dark gradient background
        - High contrast text for accessibility
        - Professional button states (active/inactive/hover)
        - Consistent spacing and typography
        """
        st.markdown("""
        <style>
        /* Sidebar container */
        section[data-testid="stSidebar"] {
            background: linear-gradient(180deg, #1e293b 0%, #334155 100%);
            width: 280px;
        }
        
        section[data-testid="stSidebar"] .block-container {
            padding: 0;
        }
        
        /* Sidebar header */
        .sidebar-header {
            padding: 2rem 1.5rem 1.5rem 1.5rem;
            border-bottom: 1px solid rgba(255, 255, 255, 0.1);
            margin-bottom: 1rem;
        }
        
        .sidebar-header h1 {
            color: #FFFFFF !important;
            font-size: 1.5rem;
            font-weight: 700;
            margin: 0 0 0.5rem 0;
            text-align: left;
        }
        
        .sidebar-header p {
            color: #D0D0D0 !important;
            font-size: 0.875rem;
            margin: 0;
            text-align: left;
        }
        
        /* Navigation sections */
        .nav-section {
            margin: 1.5rem 0 0.75rem 0;
        }
        
        .nav-label {
            color: #B0B0B0 !important;
            font-size: 0.75rem;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            padding: 0 1.5rem;
            margin-bottom: 0.5rem;
        }
        
        /* Button styling - Remove ALL focus/active states */
        section[data-testid="stSidebar"] button {
            width: calc(100% - 1.5rem) !important;
            margin: 0.125rem 0.75rem !important;
            padding: 0.875rem 1.25rem !important;
            border-radius: 0.5rem !important;
            border: none !important;
            font-weight: 500 !important;
            font-size: 0.875rem !important;
            transition: all 0.15s ease !important;
            text-align: left !important;
            height: 44px !important;
            display: flex !important;
            align-items: center !important;
            outline: none !important;
            box-shadow: none !important;
        }
        
        /* Remove focus/active states */
        section[data-testid="stSidebar"] button:focus,
        section[data-testid="stSidebar"] button:active,
        section[data-testid="stSidebar"] button:focus-visible {
            outline: none !important;
            box-shadow: none !important;
            border: none !important;
        }
        
        /* Inactive button (secondary) */
        section[data-testid="stSidebar"] button[kind="secondary"] {
            background-color: transparent !important;
            color: #E0E0E0 !important;
            border-left: 3px solid transparent !important;
        }
        
        section[data-testid="stSidebar"] button[kind="secondary"]:hover {
            background-color: rgba(255, 255, 255, 0.08) !important;
            color: #FFFFFF !important;
            border-left: 3px solid rgba(59, 130, 246, 0.5) !important;
        }
        
        section[data-testid="stSidebar"] button[kind="secondary"]:focus,
        section[data-testid="stSidebar"] button[kind="secondary"]:active {
            background-color: transparent !important;
            color: #E0E0E0 !important;
            border-left: 3px solid transparent !important;
            outline: none !important;
            box-shadow: none !important;
        }
        
        /* Active button (primary) */
        section[data-testid="stSidebar"] button[kind="primary"] {
            background-color: rgba(59, 130, 246, 0.15) !important;
            color: #FFFFFF !important;
            border-left: 3px solid #3b82f6 !important;
            font-weight: 600 !important;
        }
        
        section[data-testid="stSidebar"] button[kind="primary"]:hover {
            background-color: rgba(59, 130, 246, 0.2) !important;
            color: #FFFFFF !important;
            border-left: 3px solid #3b82f6 !important;
        }
        
        section[data-testid="stSidebar"] button[kind="primary"]:focus,
        section[data-testid="stSidebar"] button[kind="primary"]:active {
            background-color: rgba(59, 130, 246, 0.15) !important;
            color: #FFFFFF !important;
            border-left: 3px solid #3b82f6 !important;
            outline: none !important;
            box-shadow: none !important;
        }
        
        /* Force all button text to be visible */
        section[data-testid="stSidebar"] button * {
            color: inherit !important;
        }
        
        /* Logout section */
        .logout-section {
            margin-top: 2rem;
            padding-top: 1rem;
            border-top: 1px solid rgba(255, 255, 255, 0.1);
        }
        
        /* Override ALL Streamlit text in sidebar */
        section[data-testid="stSidebar"] * {
            color: #E0E0E0 !important;
        }
        
        section[data-testid="stSidebar"] h1,
        section[data-testid="stSidebar"] h2,
        section[data-testid="stSidebar"] h3 {
            color: #FFFFFF !important;
        }
        
        section[data-testid="stSidebar"] button {
            color: #E0E0E0 !important;
        }
        
        section[data-testid="stSidebar"] button[kind="primary"] {
            color: #FFFFFF !important;
        }
        
        section[data-testid="stSidebar"] .sidebar-header {
            display: block !important;
        }
        
        section[data-testid="stSidebar"] .nav-section {
            display: block !important;
        }
        
        section[data-testid="stSidebar"] .logout-section {
            display: block !important;
        }
        </style>
        """, unsafe_allow_html=True)

if __name__ == "__main__":
    app = FinanceApp()
    app.run()