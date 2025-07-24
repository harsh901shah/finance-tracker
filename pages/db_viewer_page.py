import streamlit as st
import pandas as pd
import sqlite3

class DBViewerPage:
    @staticmethod
    def show():
        st.header("Database Viewer")
        
        # Connect to the database
        conn = sqlite3.connect('finance_tracker.db')
        
        # Get list of tables
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = [table[0] for table in cursor.fetchall()]
        
        # Table selection
        selected_table = st.selectbox("Select Table", tables)
        
        if selected_table:
            # Get table data
            df = pd.read_sql_query(f"SELECT * FROM {selected_table}", conn)
            
            # Display table data
            st.subheader(f"Table: {selected_table}")
            st.dataframe(df)
            
            # Show row count
            st.text(f"Total rows: {len(df)}")
            
            # Add option to delete data
            if st.button(f"Delete All Data from {selected_table}"):
                cursor.execute(f"DELETE FROM {selected_table}")
                conn.commit()
                st.success(f"All data deleted from {selected_table}")
                st.rerun()
        
        # Close connection
        conn.close()