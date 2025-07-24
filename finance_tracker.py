"""
Main entry point for the Finance Tracker application.

This module initializes and runs the Finance Tracker application, handling
authentication, page navigation, and overall application flow.
"""

import streamlit as st
import os
import traceback
from pages.dashboard_page import DashboardPage
from pages.networth_page import NetWorthPage
from pages.transaction_page import TransactionPage
from pages.budget_page import BudgetPage
from pages.settings_page import SettingsPage
from pages.document_upload_page import DocumentUploadPage
from pages.db_viewer_page import DBViewerPage
from pages.login_page import LoginPage
from services.database_service import DatabaseService
from services.auth_service import AuthService
from services.logger_service import LoggerService

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
            "Transactions": TransactionPage.show_list,
            "Add Transaction": TransactionPage.show_add,
            "Budget": BudgetPage,
            "Upload Documents": DocumentUploadPage,
            "Settings": SettingsPage,
            "DB Viewer": DBViewerPage
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
            # Handle file permission errors
            error_msg = f"Database initialization error: {str(e)}"
            self.logger.error(error_msg)
            st.error(error_msg)
            st.info("Please check your file permissions and try again.")
        except Exception as e:
            # Handle any other unexpected errors
            error_msg = f"Unexpected error initializing database: {str(e)}"
            self.logger.error(f"{error_msg}\n{traceback.format_exc()}")
            st.error(error_msg)
            st.info("The application may not function correctly. Please restart the application.")

    
    def run(self):
        """
        Run the Finance Tracker application.
        
        Handles authentication flow, page navigation, and renders
        the appropriate page based on user selection.
        """
        try:
            self.logger.info("Starting Finance Tracker application")
            
            # Initialize session state for authentication
            if "authenticated" not in st.session_state:
                st.session_state.authenticated = False
            if "user" not in st.session_state:
                st.session_state.user = None
                
            # Check authentication status
            is_authenticated = LoginPage.verify_authentication()
            
            if not is_authenticated:
                # Show login page if not authenticated
                is_authenticated = LoginPage.show()
                
            if is_authenticated:
                # User is authenticated, show the main app
                
                # Apply custom CSS for sidebar
                self._apply_sidebar_css()
                
                # Sidebar for navigation
                with st.sidebar:
                    st.markdown("<div class='sidebar-header'>", unsafe_allow_html=True)
                    st.markdown("<h1>Finance Tracker</h1>", unsafe_allow_html=True)
                    st.markdown("</div>", unsafe_allow_html=True)
                    
                    # Display user information
                    st.markdown("<div class='sidebar-user'>", unsafe_allow_html=True)
                    st.markdown(f"<p>Welcome, <strong>{st.session_state.user['full_name']}</strong></p>", unsafe_allow_html=True)
                    st.markdown("</div>", unsafe_allow_html=True)
                    
                    st.markdown("<div class='sidebar-nav'>", unsafe_allow_html=True)
                    
                    # Navigation items with icons
                    nav_items = {
                        "Dashboard": "📊",
                        "Net Worth": "💰",
                        "Transactions": "📝",
                        "Add Transaction": "➕",
                        "Budget": "📈",
                        "Upload Documents": "📄",
                        "Settings": "⚙️",
                        "DB Viewer": "🔍"
                    }
                    
                    selected_page = None
                    
                    # Create navigation buttons
                    for page_name, icon in nav_items.items():
                        if st.sidebar.button(f"{icon} {page_name}", key=f"nav_{page_name}", use_container_width=True):
                            selected_page = page_name
                    
                    # Default to Dashboard if no page is selected
                    if selected_page is None:
                        if "current_page" in st.session_state:
                            selected_page = st.session_state.current_page
                        else:
                            selected_page = "Dashboard"
                    
                    # Store current page in session state
                    st.session_state.current_page = selected_page
                    
                    st.markdown("</div>", unsafe_allow_html=True)
                    
                    # Logout button at the bottom
                    st.markdown("<div class='sidebar-footer'>", unsafe_allow_html=True)
                    if st.button("Logout", key="logout_button", use_container_width=True):
                        # Handle logout
                        if "user" in st.session_state and st.session_state.user and "session_token" in st.session_state.user:
                            AuthService.logout(st.session_state.user["session_token"])
                        st.session_state.user = None
                        st.session_state.authenticated = False
                        st.rerun()
                    st.markdown("</div>", unsafe_allow_html=True)
            
                # Display the selected page
                try:
                    page = selected_page
                    if page == "Add Transaction":
                        self.pages[page]()
                    elif page == "Transactions":
                        self.pages[page]()
                    else:
                        self.pages[page].show()
                except Exception as e:
                    # Handle errors when displaying pages
                    error_msg = f"Error displaying page: {str(e)}"
                    self.logger.error(f"{error_msg}\n{traceback.format_exc()}")
                    st.error(error_msg)
                    st.info("Please try refreshing the page or selecting a different section.")
                    
                    # Show technical details in an expander for debugging
                    with st.expander("Technical Details"):
                        st.code(str(e))
                        st.code(traceback.format_exc())
        except Exception as e:
            # Handle any unexpected application errors
            error_msg = f"Unexpected application error: {str(e)}"
            self.logger.error(f"{error_msg}\n{traceback.format_exc()}")
            st.error(error_msg)
            st.error("The application encountered an unexpected error. Please refresh the page or restart the application.")
            
            # Show technical details in an expander for debugging
            with st.expander("Technical Details"):
                st.code(str(e))
                st.code(traceback.format_exc())
    
    @staticmethod
    def _apply_sidebar_css():
        """
        Apply custom CSS for styling the sidebar.
        
        Adds styles for the sidebar layout, navigation buttons,
        user information display, and logout button.
        """
        st.markdown("""
        <style>
        /* Sidebar styling */
        section[data-testid="stSidebar"] {
            background-color: #2C3E50;
            color: white;
            width: 250px;
        }
        
        section[data-testid="stSidebar"] button {
            background-color: transparent;
            color: white;
            text-align: left;
            font-weight: normal;
            padding: 0.5rem 0;
            border-radius: 5px;
            border: none;
            margin: 0.25rem 0;
        }
        
        section[data-testid="stSidebar"] button:hover {
            background-color: rgba(255, 255, 255, 0.1);
        }
        
        /* Sidebar header */
        .sidebar-header {
            padding: 1.5rem 0;
            margin-bottom: 1rem;
            border-bottom: 1px solid rgba(255, 255, 255, 0.1);
        }
        
        .sidebar-header h1 {
            color: white;
            font-size: 1.5rem;
            font-weight: 600;
            margin: 0;
        }
        
        /* Sidebar user section */
        .sidebar-user {
            padding-bottom: 1rem;
            margin-bottom: 1rem;
            border-bottom: 1px solid rgba(255, 255, 255, 0.1);
        }
        
        .sidebar-user p {
            color: rgba(255, 255, 255, 0.8);
            margin: 0;
        }
        
        /* Sidebar navigation */
        .sidebar-nav {
            margin-bottom: 2rem;
        }
        
        /* Sidebar footer */
        .sidebar-footer {
            position: absolute;
            bottom: 1rem;
            width: 100%;
            padding-right: 2rem;
        }
        
        /* Logout button */
        .sidebar-footer button {
            background-color: #E74C3C !important;
            color: white !important;
            text-align: center !important;
            font-weight: 500 !important;
        }
        
        .sidebar-footer button:hover {
            background-color: #C0392B !important;
        }
        </style>
        """, unsafe_allow_html=True)

if __name__ == "__main__":
    app = FinanceApp()
    app.run()