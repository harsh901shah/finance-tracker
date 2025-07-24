import streamlit as st
import pandas as pd
import os
import sys
import subprocess
from services.document_parser_service import DocumentParserService
from services.statement_processor import StatementProcessor

class DocumentUploadPage:
    @staticmethod
    def show():
        st.header("Upload Financial Documents")
        
        # Document type selection
        doc_type = st.selectbox(
            "Document Type",
            ["Bank Statement", "Credit Card Statement", "Brokerage Statement"]
        )
        
        # Account type selection for bank statements
        if doc_type == "Bank Statement":
            account_type = st.selectbox(
                "Account Type",
                ["Checking", "Savings", "Money Market", "Other"]
            )
        else:
            account_type = None
        
        # File upload
        uploaded_file = st.file_uploader(
            "Choose a file",
            type=["csv", "xls", "xlsx", "pdf"]
        )
        
        if uploaded_file and st.button("Parse Document"):
            try:
                # Parse document
                with st.spinner("Parsing document..."):
                    transactions, detected_type = DocumentParserService.parse_document(
                        uploaded_file,
                        uploaded_file.name,
                        doc_type.lower().split()[0]
                    )
                
                # Show results
                st.success(f"Detected: {detected_type.title()} Statement")
                
                # Check for statement metadata
                metadata = None
                for transaction in transactions:
                    if "statement_metadata" in transaction:
                        metadata = transaction["statement_metadata"]
                        break
                
                # Update metadata with account type if provided
                if metadata and account_type and doc_type == "Bank Statement":
                    metadata["account_type"] = account_type.lower()
                    
                    # Update the metadata in all transactions
                    for transaction in transactions:
                        if "statement_metadata" in transaction:
                            transaction["statement_metadata"]["account_type"] = account_type.lower()
                        if "additional_data" in transaction and isinstance(transaction["additional_data"], dict):
                            if "statement_metadata" in transaction["additional_data"]:
                                transaction["additional_data"]["statement_metadata"]["account_type"] = account_type.lower()
                    
                    # Process metadata ONLY ONCE to update net worth
                    success = StatementProcessor.process_statement_metadata(metadata)
                    if not success:
                        # Get month name from statement period or current month
                        month_name = "this month"
                        statement_period = metadata.get('statement_period', '')
                        if statement_period:
                            import re
                            match = re.search(r'to\s+([A-Za-z]+)', statement_period)
                            if match:
                                month_name = match.group(1)
                        
                        st.error(f"⚠️ DUPLICATE STATEMENT DETECTED ⚠️\n\nA statement for {metadata.get('bank', 'this bank')} {metadata.get('account_type', '').title()} Account {metadata.get('account_number', '')} has already been processed for {month_name}.\n\nPlease upload a different statement or try again next month.")
                        return
                
                # Display statement summary if metadata is available
                if metadata:
                    st.subheader("Statement Summary")
                    
                    col1, col2 = st.columns(2)
                    
                    # Column 1: Bank and account info
                    if "bank" in metadata:
                        col1.metric("Bank", metadata["bank"])
                    if "account_holder" in metadata:
                        col1.metric("Account Holder", metadata["account_holder"])
                    if "account_number" in metadata:
                        col1.metric("Account Number", metadata["account_number"])
                    if "statement_period" in metadata:
                        col1.metric("Statement Period", metadata["statement_period"])
                    if "account_type" in metadata:
                        col1.metric("Account Type", metadata["account_type"].title())
                    
                    # Column 2: Balance info
                    if "beginning_balance" in metadata:
                        col2.metric("Beginning Balance", f"${metadata['beginning_balance']:.2f}")
                    if "ending_balance" in metadata:
                        col2.metric("Ending Balance", f"${metadata['ending_balance']:.2f}")
                    if "deposits" in metadata:
                        col2.metric("Total Deposits", f"${metadata['deposits']:.2f}")
                    if "withdrawals" in metadata:
                        col2.metric("Total Withdrawals", f"${abs(metadata['withdrawals']):.2f}")
                
                # Show transactions
                if transactions:
                    st.subheader(f"Found {len(transactions)} Transactions")
                    
                    # Create DataFrame for display
                    display_df = pd.DataFrame(transactions)
                    
                    # Remove metadata column for display
                    if "statement_metadata" in display_df.columns:
                        display_df = display_df.drop(columns=["statement_metadata"])
                    
                    # Display transactions
                    st.dataframe(
                        display_df,
                        column_config={
                            "amount": st.column_config.NumberColumn(
                                "Amount ($)",
                                format="$%.2f",
                            ),
                        },
                        hide_index=True,
                        use_container_width=True
                    )
                    
                    # Import button
                    if st.button("Import Transactions"):
                        count = DocumentParserService.save_transactions_to_db(transactions)
                        st.success(f"Imported {count} transactions")
                else:
                    st.warning("No transactions found")
            except Exception as e:
                st.error(f"Error: {str(e)}")
                
                # Check for PDF library errors
                error_msg = str(e)
                if "pdfminer" in error_msg or "PyPDF2" in error_msg or "pdfplumber" in error_msg:
                    st.error("PDF parsing libraries are missing")
                    
                    if st.button("Install PDF Libraries"):
                        with st.spinner("Installing..."):
                            try:
                                subprocess.check_call([
                                    sys.executable, "-m", "pip", "install", 
                                    "pdfplumber", "PyPDF2"
                                ])
                                st.success("Installation successful! Please refresh the page.")
                            except Exception as e:
                                st.error(f"Installation failed: {e}")
                                st.info("Try running: pip install pdfplumber PyPDF2")