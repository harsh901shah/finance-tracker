import streamlit as st
import pandas as pd
import plotly.express as px
from services.financial_data_service import NetWorthService

class NetWorthPage:
    """Net Worth page showing assets and liabilities"""
    
    @staticmethod
    def show():
        st.header("Net Worth Summary")
        
        # Load net worth data
        networth_data = NetWorthService.load_networth()
        
        if not networth_data:
            st.info("No net worth data found. Add your assets and liabilities to see your net worth summary.")
            
            # Add sample data button
            if st.button("Load Sample Data"):
                with open('networth.json', 'r') as f:
                    import json
                    sample_data = json.load(f)
                NetWorthService.save_networth(sample_data)
                st.success("Sample data loaded successfully!")
                st.experimental_rerun()
            return
        
        # Calculate total values
        total_assets = 0
        total_debts = 0
        
        # Calculate investments
        investments = networth_data.get('investments', {})
        stocks_value = sum(item['value'] for item in investments.get('stocks', []))
        savings_value = sum(item['value'] for item in investments.get('savings', []))
        retirement_value = sum(item['value'] for item in investments.get('retirement', []))
        hsa_value = sum(item['value'] for item in investments.get('hsa', []))
        precious_metals_value = sum(item['value'] for item in investments.get('precious_metals', []))
        
        # Calculate debts
        debts = networth_data.get('debts', {})
        loans_value = sum(item['value'] for item in debts.get('loans', []))
        credit_cards_value = sum(item['value'] for item in debts.get('credit_cards', []))
        mortgage_value = sum(item['value'] for item in debts.get('mortgage', []))
        
        # Calculate real estate
        real_estate = networth_data.get('real_estate', [])
        real_estate_value = sum(item['current_value'] for item in real_estate)
        
        # Total assets and debts
        total_assets = stocks_value + savings_value + retirement_value + hsa_value + precious_metals_value + real_estate_value
        total_debts = loans_value + credit_cards_value + mortgage_value
        net_worth = total_assets - total_debts
        
        # Display summary metrics
        st.subheader("Financial Overview")
        col1, col2, col3 = st.columns(3)
        col1.metric("Total Assets", f"${total_assets:,.2f}")
        col2.metric("Total Liabilities", f"${total_debts:,.2f}")
        col3.metric("Net Worth", f"${net_worth:,.2f}")
        
        # Display asset breakdown
        st.subheader("Asset Breakdown")
        
        # Create asset data for visualization
        asset_data = {
            'Category': ['Stocks', 'Savings', 'Retirement', 'HSA', 'Precious Metals', 'Real Estate'],
            'Value': [stocks_value, savings_value, retirement_value, hsa_value, precious_metals_value, real_estate_value]
        }
        asset_df = pd.DataFrame(asset_data)
        
        # Create asset visualization
        fig = px.pie(
            asset_df, 
            values='Value', 
            names='Category', 
            title='Asset Distribution',
            hole=0.4
        )
        st.plotly_chart(fig, use_container_width=True)
        
        # Display detailed breakdown by category
        tab1, tab2, tab3, tab4, tab5 = st.tabs(["Investments", "Savings", "Retirement", "Real Estate", "Debts"])
        
        with tab1:
            NetWorthPage._show_investments_tab(investments)
        
        with tab2:
            NetWorthPage._show_savings_tab(investments)
        
        with tab3:
            NetWorthPage._show_retirement_tab(investments)
        
        with tab4:
            NetWorthPage._show_real_estate_tab(real_estate)
        
        with tab5:
            NetWorthPage._show_debts_tab(debts)
    
    @staticmethod
    def _show_investments_tab(investments):
        st.subheader("Investment Accounts")
        if investments.get('stocks'):
            stocks_df = pd.DataFrame(investments['stocks'])
            st.dataframe(
                stocks_df,
                column_config={
                    "name": "Account",
                    "value": st.column_config.NumberColumn("Value ($)", format="$%d"),
                    "owner": "Owner"
                },
                hide_index=True,
                use_container_width=True
            )
            
            # Show by owner
            st.subheader("Investments by Owner")
            owner_data = stocks_df.groupby('owner')['value'].sum().reset_index()
            fig = px.bar(owner_data, x='owner', y='value', title='Investment Value by Owner')
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No investment accounts found.")
    
    @staticmethod
    def _show_savings_tab(investments):
        st.subheader("Savings Accounts")
        if investments.get('savings'):
            savings_df = pd.DataFrame(investments['savings'])
            st.dataframe(
                savings_df,
                column_config={
                    "name": "Account",
                    "value": st.column_config.NumberColumn("Value ($)", format="$%d"),
                    "owner": "Owner"
                },
                hide_index=True,
                use_container_width=True
            )
        else:
            st.info("No savings accounts found.")
            
        # Show precious metals if any
        if investments.get('precious_metals'):
            st.subheader("Precious Metals")
            metals_df = pd.DataFrame(investments['precious_metals'])
            st.dataframe(
                metals_df,
                column_config={
                    "name": "Type",
                    "value": st.column_config.NumberColumn("Value ($)", format="$%d"),
                    "owner": "Owner"
                },
                hide_index=True,
                use_container_width=True
            )
    
    @staticmethod
    def _show_retirement_tab(investments):
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Retirement Accounts")
            if investments.get('retirement'):
                retirement_df = pd.DataFrame(investments['retirement'])
                st.dataframe(
                    retirement_df,
                    column_config={
                        "name": "Account",
                        "value": st.column_config.NumberColumn("Value ($)", format="$%d"),
                        "owner": "Owner"
                    },
                    hide_index=True,
                    use_container_width=True
                )
            else:
                st.info("No retirement accounts found.")
        
        with col2:
            st.subheader("HSA Accounts")
            if investments.get('hsa'):
                hsa_df = pd.DataFrame(investments['hsa'])
                st.dataframe(
                    hsa_df,
                    column_config={
                        "name": "Account",
                        "value": st.column_config.NumberColumn("Value ($)", format="$%d"),
                        "owner": "Owner"
                    },
                    hide_index=True,
                    use_container_width=True
                )
            else:
                st.info("No HSA accounts found.")
    
    @staticmethod
    def _show_real_estate_tab(real_estate):
        st.subheader("Real Estate")
        if real_estate:
            real_estate_df = pd.DataFrame(real_estate)
            st.dataframe(
                real_estate_df,
                column_config={
                    "name": "Property",
                    "purchase_value": st.column_config.NumberColumn("Purchase Value ($)", format="$%d"),
                    "current_value": st.column_config.NumberColumn("Current Value ($)", format="$%d"),
                    "owner": "Owner"
                },
                hide_index=True,
                use_container_width=True
            )
            
            # Calculate equity
            for i, property in enumerate(real_estate):
                equity = property['current_value'] - property.get('purchase_value', 0)
                appreciation = equity / property.get('purchase_value', 1) * 100
                st.metric(
                    f"Equity in {property['name']}", 
                    f"${equity:,.2f}", 
                    f"{appreciation:.1f}%"
                )
        else:
            st.info("No real estate properties found.")
    
    @staticmethod
    def _show_debts_tab(debts):
        st.subheader("Debts & Liabilities")
        
        # Auto loans
        if debts.get('loans'):
            st.subheader("Auto Loans")
            loans_df = pd.DataFrame(debts['loans'])
            st.dataframe(
                loans_df,
                column_config={
                    "name": "Loan",
                    "value": st.column_config.NumberColumn("Balance ($)", format="$%d"),
                    "owner": "Owner"
                },
                hide_index=True,
                use_container_width=True
            )
        
        # Credit cards
        if debts.get('credit_cards'):
            st.subheader("Credit Cards")
            cc_df = pd.DataFrame(debts['credit_cards'])
            st.dataframe(
                cc_df,
                column_config={
                    "name": "Card",
                    "value": st.column_config.NumberColumn("Balance ($)", format="$%d"),
                    "owner": "Owner"
                },
                hide_index=True,
                use_container_width=True
            )
        
        # Mortgage
        if debts.get('mortgage'):
            st.subheader("Mortgage")
            mortgage_df = pd.DataFrame(debts['mortgage'])
            st.dataframe(
                mortgage_df,
                column_config={
                    "name": "Mortgage",
                    "value": st.column_config.NumberColumn("Balance ($)", format="$%d"),
                    "owner": "Owner"
                },
                hide_index=True,
                use_container_width=True
            )