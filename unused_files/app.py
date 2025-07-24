import streamlit as st
import os
from pages.dashboard_page import DashboardPage
from pages.networth_page import NetWorthPage
from pages.transaction_page import TransactionPage
from pages.budget_page import BudgetPage
from pages.settings_page import SettingsPage
from pages.document_upload_page import DocumentUploadPage
from services.database_service import DatabaseService

# Set page configuration
st.set_page_config(
    page_title="Personal Finance Tracker",
    page_icon="💰",
    layout="wide"
)

class FinanceApp:
    """Main Finance Tracker Application"""
    
    def __init__(self):
        """Initialize the application"""
        # Initialize database
        self._initialize_database()
        
        self.pages = {
            "Dashboard": DashboardPage,
            "Net Worth": NetWorthPage,
            "Add Transaction": TransactionPage.show_add,
            "Transactions": TransactionPage.show_list,
            "Upload Documents": DocumentUploadPage,
            "Budget": BudgetPage,
            "Settings": SettingsPage
        }
    
    def _initialize_database(self):
        """Initialize the database"""
        try:
            # Create database tables
            DatabaseService.initialize_database()
        except IOError as e:
            st.error(f"Database initialization error: {str(e)}")
            st.info("Please check your file permissions and try again.")
        except Exception as e:
            st.error(f"Unexpected error initializing database: {str(e)}")
            st.info("The application may not function correctly. Please restart the application.")
    
    def run(self):
        """Run the application"""
        st.title("💰 Personal Finance Tracker")
        
        # Sidebar for navigation
        with st.sidebar:
            st.header("Navigation")
            page = st.radio("Go to", list(self.pages.keys()))
        
        # Display the selected page
        try:
            if page == "Add Transaction":
                self.pages[page]()
            elif page == "Transactions":
                self.pages[page]()
            else:
                self.pages[page].show()
        except Exception as e:
            st.error(f"Error displaying page: {str(e)}")
            st.info("Please try refreshing the page or selecting a different section.")
            
            # Show technical details in an expander for debugging
            with st.expander("Technical Details"):
                st.code(str(e))
                import traceback
                st.code(traceback.format_exc())

if __name__ == "__main__":
    app = FinanceApp()
    app.run()