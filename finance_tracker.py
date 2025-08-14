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
from pages.add_transaction_page import AddTransactionPage
from pages.budget_page import BudgetPage
from pages.login_page import LoginPage
from services.database_service import DatabaseService
from services.auth_service import AuthService
from services.logger_service import LoggerService
from components.onboarding import OnboardingGuide
from components.user_profile import UserProfile
from utils.auth_middleware import AuthMiddleware

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
            "Add Transaction": AddTransactionPage,
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
                # Show login page if not authenticated - NO SIDEBAR
                is_authenticated = LoginPage.show()
                
            if is_authenticated:
                # User is authenticated, show the main app with sidebar
                
                # Apply custom CSS for sidebar
                self._apply_sidebar_css()
                
                # Sidebar for navigation - ONLY when authenticated
                with st.sidebar:
                    # Get personalized display name
                    display_name = UserProfile.get_user_display_name()
                    st.markdown(f'<div class="sidebar-header"><h1>💰 Finance Tracker</h1><p>Welcome, {display_name}</p></div>', unsafe_allow_html=True)
                    
                    # Get current page or default to Dashboard
                    if "current_page" not in st.session_state:
                        st.session_state.current_page = "Dashboard"
                    
                    current_page = st.session_state.current_page
                    selected_page = None
                    
                    # Overview section - Main dashboard and financial summary pages
                    st.markdown('<div class="nav-section"><div class="nav-label">OVERVIEW</div></div>', unsafe_allow_html=True)
                    if st.sidebar.button("Dashboard", key="nav_Dashboard", use_container_width=True, type="primary" if current_page == "Dashboard" else "secondary"):
                        selected_page = "Dashboard"
                        st.session_state.current_page = "Dashboard"
                        st.rerun()  # Force page refresh to update active button styling
                    if st.sidebar.button("Net Worth", key="nav_Net_Worth", use_container_width=True, type="primary" if current_page == "Net Worth" else "secondary"):
                        selected_page = "Net Worth"
                        st.session_state.current_page = "Net Worth"
                        st.rerun()
                    
                    # Transactions section - Core transaction management functionality
                    st.markdown('<div class="nav-section"><div class="nav-label">TRANSACTIONS</div></div>', unsafe_allow_html=True)
                    if st.sidebar.button("View Transactions", key="nav_View_Transactions", use_container_width=True, type="primary" if current_page == "View Transactions" else "secondary"):
                        selected_page = "View Transactions"
                        st.session_state.current_page = "View Transactions"
                        st.rerun()
                    if st.sidebar.button("Add Transaction", key="nav_Add_Transaction", use_container_width=True, type="primary" if current_page == "Add Transaction" else "secondary"):
                        selected_page = "Add Transaction"
                        st.session_state.current_page = "Add Transaction"
                        st.rerun()
                    if st.sidebar.button("Budget", key="nav_Budget", use_container_width=True, type="primary" if current_page == "Budget" else "secondary"):
                        selected_page = "Budget"
                        st.session_state.current_page = "Budget"
                        st.rerun()
                    

                    
                    # Use current page for display
                    selected_page = current_page
                    
                    # End of navigation
                    
                    # Logout button
                    st.markdown('<div class="logout-section"></div>', unsafe_allow_html=True)
                    if st.sidebar.button("Logout", key="logout_button", use_container_width=True, type="secondary"):
                        if "user" in st.session_state and st.session_state.user and "session_token" in st.session_state.user:
                            AuthService.logout(st.session_state.user["session_token"])
                        st.session_state.user = None
                        st.session_state.authenticated = False
                        st.rerun()
            
                # Show onboarding for new users
                OnboardingGuide.show_welcome_tour()
                
                # Display the selected page with security check
                try:
                    # Ensure user is still authenticated before showing pages
                    if not AuthMiddleware.is_authenticated():
                        st.error("🔒 Session expired. Please login again.")
                        st.session_state.authenticated = False
                        st.rerun()
                        return
                    
                    page = selected_page
                    
                    # Show contextual tooltip for current page
                    OnboardingGuide.show_page_tooltip(page)
                    
                    # Render the page
                    if page == "Add Transaction":
                        self.pages[page].show()
                    elif page == "View Transactions":
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
        
        /* Button styling */
        section[data-testid="stSidebar"] button {
            width: calc(100% - 1.5rem);
            margin: 0.125rem 0.75rem;
            padding: 0.875rem 1.25rem;
            border-radius: 0.5rem;
            border: none;
            font-weight: 500;
            font-size: 0.875rem;
            transition: all 0.15s ease;
            text-align: left;
            height: 44px;
            display: flex;
            align-items: center;
        }
        
        /* Force button text colors */
        section[data-testid="stSidebar"] button[kind="secondary"] {
            background-color: transparent !important;
            color: #E0E0E0 !important;
            border-left: 3px solid transparent;
        }
        
        section[data-testid="stSidebar"] button[kind="secondary"]:hover {
            background-color: rgba(255, 255, 255, 0.08) !important;
            color: #FFFFFF !important;
            border-left: 3px solid rgba(59, 130, 246, 0.5);
        }
        
        section[data-testid="stSidebar"] button[kind="primary"] {
            background-color: rgba(59, 130, 246, 0.15) !important;
            color: #FFFFFF !important;
            border-left: 3px solid #3b82f6;
            font-weight: 600;
        }
        
        section[data-testid="stSidebar"] button[kind="primary"]:hover {
            background-color: rgba(59, 130, 246, 0.2) !important;
            color: #FFFFFF !important;
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