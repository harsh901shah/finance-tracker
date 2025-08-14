import streamlit as st
import pandas as pd
from services.financial_data_service import TransactionService

class SettingsPage:
    """Settings page for application configuration"""
    
    @staticmethod
    def show():
        st.header("Settings")
        
        st.subheader("Data Management")
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("Export Data"):
                # Create a download link for the data
                transactions = TransactionService.load_transactions()
                df = pd.DataFrame(transactions)
                csv = df.to_csv(index=False)
                st.download_button(
                    label="Download CSV",
                    data=csv,
                    file_name="finance_tracker_data.csv",
                    mime="text/csv"
                )
        
        with col2:
            if st.button("Clear All Data"):
                st.warning("This will delete all your transaction data. This action cannot be undone.")
                if st.button("Yes, I'm sure"):
                    TransactionService.save_transactions([])
                    st.success("All data has been cleared.")