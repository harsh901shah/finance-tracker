import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime
from services.financial_data_service import BudgetService, TransactionService

class BudgetPage:
    """Budget page for setting and tracking budgets"""
    
    @staticmethod
    def show():
        st.header("Budget Planning")
        
        # Define categories
        categories = ["Food", "Transportation", "Housing", "Utilities", "Entertainment", 
                     "Healthcare", "Education", "Shopping", "Other"]
        
        # Load budget data
        budget_data = BudgetService.load_budget()
        if not budget_data:
            budget_data = {category: 0 for category in categories}
        
        # Monthly budget setup
        st.subheader("Set Monthly Budget")
        
        # Budget form
        with st.form("budget_form"):
            col1, col2 = st.columns(2)
            
            updated_budget = {}
            for i, category in enumerate(categories):
                with col1 if i < len(categories)/2 else col2:
                    updated_budget[category] = st.number_input(
                        f"{category} Budget ($)", 
                        min_value=0.0, 
                        value=float(budget_data.get(category, 0)),
                        step=10.0
                    )
            
            submitted = st.form_submit_button("Update Budget")
            
            if submitted:
                BudgetService.save_budget(updated_budget)
                st.success("Budget updated successfully!")
                budget_data = updated_budget
        
        # Budget vs Actual Spending
        st.subheader("Budget vs Actual Spending")
        
        # Load transactions
        transactions = TransactionService.load_transactions()
        
        if not transactions:
            st.info("No transactions found. Add some transactions to see budget comparison.")
            return
        
        # Get current month's expenses
        df = pd.DataFrame(transactions)
        if 'date' in df.columns and 'category' in df.columns:
            df['date'] = pd.to_datetime(df['date'])
            current_month = datetime.now().strftime('%Y-%m')
            current_month_expenses = df[
                (df['date'].dt.strftime('%Y-%m') == current_month) & 
                (df['type'] == 'Expense')
            ]
            
            if not current_month_expenses.empty:
                expenses_by_category = current_month_expenses.groupby('category')['amount'].sum().to_dict()
                
                # Create comparison data
                comparison_data = []
                for category in categories:
                    budget_amount = budget_data.get(category, 0)
                    spent_amount = expenses_by_category.get(category, 0)
                    remaining = budget_amount - spent_amount
                    percentage = (spent_amount / budget_amount * 100) if budget_amount > 0 else 0
                    
                    comparison_data.append({
                        "Category": category,
                        "Budget": budget_amount,
                        "Spent": spent_amount,
                        "Remaining": remaining,
                        "Percentage": percentage
                    })
                
                comparison_df = pd.DataFrame(comparison_data)
                
                # Display as table
                st.dataframe(
                    comparison_df,
                    column_config={
                        "Budget": st.column_config.NumberColumn("Budget ($)", format="$%.2f"),
                        "Spent": st.column_config.NumberColumn("Spent ($)", format="$%.2f"),
                        "Remaining": st.column_config.NumberColumn("Remaining ($)", format="$%.2f"),
                        "Percentage": st.column_config.ProgressColumn(
                            "% of Budget Used",
                            min_value=0,
                            max_value=100,
                            format="%.1f%%"
                        ),
                    },
                    hide_index=True,
                    use_container_width=True
                )
                
                # Visualization
                fig = go.Figure()
                
                for category in categories:
                    budget_amount = budget_data.get(category, 0)
                    spent_amount = expenses_by_category.get(category, 0)
                    
                    if budget_amount > 0:  # Only show categories with a budget
                        fig.add_trace(go.Bar(
                            name='Budget',
                            x=[category],
                            y=[budget_amount],
                            marker_color='lightblue'
                        ))
                        
                        fig.add_trace(go.Bar(
                            name='Spent',
                            x=[category],
                            y=[spent_amount],
                            marker_color='coral'
                        ))
                
                fig.update_layout(
                    title='Budget vs Actual by Category',
                    barmode='group',
                    xaxis_title='Category',
                    yaxis_title='Amount ($)'
                )
                
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info(f"No expenses recorded for the current month ({current_month}).")
        else:
            st.info("Add categorized transactions to see budget comparison.")