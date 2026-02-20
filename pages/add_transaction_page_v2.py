import streamlit as st
from datetime import datetime, date
from services.database_service import DatabaseService
from services.template_service import TemplateService
from services.tooltip_service import TooltipService
from components.dynamic_form_builder import DynamicFormBuilder
from components.user_preferences import UserPreferencesManager
from utils.auth_middleware import AuthMiddleware
from config.app_config import AppConfig

class AddTransactionPageV2:
    """Dynamic add transaction page using templates"""
    
    @staticmethod
    def show():
        # Display flash messages
        if 'flash_success' in st.session_state:
            st.success(st.session_state['flash_success'])
            del st.session_state['flash_success']
        
        if 'flash_error' in st.session_state:
            st.error(st.session_state['flash_error'])
            del st.session_state['flash_error']
        
        # Apply custom CSS
        AddTransactionPageV2._apply_custom_css()
        
        st.header("💰 Add Transaction")
        
        # Get current user
        current_user = AuthMiddleware.get_current_user_id()
        if not current_user:
            st.error("🔒 Please login to add transactions")
            return
        user_id = str(current_user.get('user_id') if isinstance(current_user, dict) else current_user)
        
        # Initialize templates
        try:
            TemplateService.initialize_templates_table()
        except Exception as e:
            st.warning(f"Template system initialization: {e}")
        
        # Load user templates
        templates = TemplateService.get_user_templates(user_id)
        
        if not templates:
            st.info("🎉 Welcome! Let's set up your transaction templates.")
            if st.button("🌱 Create Default Templates", type="primary"):
                TemplateService.seed_default_templates(user_id)
                st.success("✅ Default templates created!")
                st.rerun()
            
            st.markdown("---")
            return
        
        # Show contextual help
        TooltipService.show_contextual_help('add_transaction')
        
        # DEBUG: Show all templates with their types
        if st.session_state.get('ft_debug_mode', False):
            with st.expander("🔧 Debug: All Templates", expanded=False):
                for t in templates:
                    st.write(f"{t.get('icon')} {t.get('template_name')} → Type: {t.get('transaction_type')} | Category: {t.get('category')}")
                
                st.markdown("---")
                if st.button("🔧 Fix Mismatched Templates"):
                    fixed_count = AddTransactionPageV2._fix_mismatched_templates(user_id, templates)
                    st.success(f"✅ Fixed {fixed_count} templates")
                    st.rerun()
        
        # Group templates by category with strict filtering
        grouped_templates = {}
        for template in templates:
            # Defensive: ensure transaction_type matches expected values
            transaction_type = template.get('transaction_type', '').strip()
            if not transaction_type:
                continue
            
            category_group = AddTransactionPageV2._get_category_group(transaction_type)
            
            # Strict validation: only add if transaction_type matches the group
            expected_type = AddTransactionPageV2._get_expected_type_for_group(category_group)
            if transaction_type != expected_type:
                # Log mismatch for debugging
                print(f"Warning: Template '{template.get('template_name')}' has type '{transaction_type}' but appears in group '{category_group}'")
                continue
            
            if category_group not in grouped_templates:
                grouped_templates[category_group] = []
            grouped_templates[category_group].append(template)
        
        # Render templates by group
        st.subheader("Quick Add")
        
        for group_name, group_templates in grouped_templates.items():
            with st.expander(group_name, expanded=(group_name == "💰 Income")):
                # Create grid layout (3 columns)
                cols = st.columns(3)
                
                for idx, template in enumerate(group_templates):
                    col_idx = idx % 3
                    with cols[col_idx]:
                        button_label = f"{template['icon']} {template['template_name']}"
                        form_key = f"template_{template['id']}"
                        
                        if st.button(button_label, width="stretch", key=f"btn_{form_key}"):
                            st.session_state[f"show_{form_key}_form"] = not st.session_state.get(f"show_{form_key}_form", False)
                        
                        # Show form inline if toggled
                        if st.session_state.get(f"show_{form_key}_form", False):
                            DynamicFormBuilder.render_template_form(template, form_key)
        
        # Monthly summary
        st.markdown("---")
        st.subheader("📊 This Month Summary")
        AddTransactionPageV2._show_monthly_summary(user_id)
    
    @staticmethod
    def _get_category_group(transaction_type: str) -> str:
        """Map transaction type to display group"""
        mapping = {
            'Income': '💰 Income',
            'Expense': '💸 Expenses',
            'Investment': '📈 Investments',
            'Transfer': '🔄 Transfers',
            'Tax': '🏛️ Taxes'
        }
        return mapping.get(transaction_type, '📦 Other')
    
    @staticmethod
    def _get_expected_type_for_group(group_name: str) -> str:
        """Reverse map: get expected transaction type for a group"""
        reverse_mapping = {
            '💰 Income': 'Income',
            '💸 Expenses': 'Expense',
            '📈 Investments': 'Investment',
            '🔄 Transfers': 'Transfer',
            '🏛️ Taxes': 'Tax',
            '📦 Other': ''
        }
        return reverse_mapping.get(group_name, '')
    
    @staticmethod
    def _fix_mismatched_templates(user_id: str, templates: list) -> int:
        """Fix templates with wrong transaction_type based on category"""
        expense_categories = {'Travel', 'Food', 'Groceries', 'Shopping', 'Entertainment', 
                            'Transportation', 'Housing', 'Bills & Utilities', 'Healthcare',
                            'Education', 'Personal Care', 'Dining', 'Credit Card'}
        
        fixed_count = 0
        for template in templates:
            category = template.get('category', '')
            current_type = template.get('transaction_type', '')
            correct_type = None
            
            if category in expense_categories:
                correct_type = 'Expense'
            elif category in {'Salary', 'Bonus', 'Gift'}:
                correct_type = 'Income'
            elif category in {'Investment', 'Retirement'}:
                correct_type = 'Investment'
            elif category in {'Savings', 'Transfer'}:
                correct_type = 'Transfer'
            elif category == 'Tax':
                correct_type = 'Tax'
            
            if correct_type and current_type != correct_type:
                TemplateService.update_template(template['id'], user_id, {'transaction_type': correct_type})
                fixed_count += 1
        
        return fixed_count
    
    @staticmethod
    def _show_monthly_summary(user_id: str):
        """Show monthly transaction summary"""
        try:
            from services.financial_data_service import TransactionService
            transactions = TransactionService.load_transactions()
            
            current_month = datetime.now().strftime('%Y-%m')
            current_transactions = [t for t in transactions if t.get('date', '').startswith(current_month)]
            
            total_income = sum(float(t.get('amount', 0)) for t in current_transactions if t.get('type') == 'Income')
            total_expenses = sum(float(t.get('amount', 0)) for t in current_transactions if t.get('type') == 'Expense')
            total_investments = sum(float(t.get('amount', 0)) for t in current_transactions if t.get('type') == 'Investment')
            total_transfers = sum(float(t.get('amount', 0)) for t in current_transactions if t.get('type') == 'Transfer')
            
            net_cash_flow = total_income - total_expenses - total_investments - total_transfers
            
            col1, col2, col3, col4, col5 = st.columns(5)
            
            with col1:
                st.metric("💰 Income", f"${total_income:,.2f}")
            with col2:
                st.metric("💸 Expenses", f"${total_expenses:,.2f}")
            with col3:
                st.metric("📈 Investments", f"${total_investments:,.2f}")
            with col4:
                st.metric("🔄 Transfers", f"${total_transfers:,.2f}")
            with col5:
                st.metric("💰 Net Cash Flow", f"${net_cash_flow:,.2f}")
            
            st.info(f"📊 {len(current_transactions)} transactions this month")
        except Exception as e:
            st.error(f"Error calculating summary: {str(e)}")
    
    @staticmethod
    def _apply_custom_css():
        """Apply custom CSS"""
        st.markdown("""
        <style>
        .stExpander {
            border: 1px solid #e0e0e0;
            border-radius: 12px;
            margin-bottom: 1.5rem;
            box-shadow: 0 2px 8px rgba(0,0,0,0.08);
        }
        .stButton > button {
            width: 100%;
            height: 48px;
            border-radius: 6px;
            transition: all 0.2s ease;
        }
        .stButton > button:hover {
            transform: translateY(-1px);
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        </style>
        """, unsafe_allow_html=True)
