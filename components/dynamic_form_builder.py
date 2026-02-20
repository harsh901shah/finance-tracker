import streamlit as st
import json
from datetime import date
from typing import Dict, Any
from services.database_service import DatabaseService
from utils.auth_middleware import AuthMiddleware

class DynamicFormBuilder:
    """Renders transaction forms dynamically from template schemas"""
    
    @staticmethod
    def render_template_form(template: Dict[str, Any], form_key: str):
        """Render a transaction form based on template"""
        with st.container():
            st.markdown(f"**{template['icon']} {template['template_name']}**")
            
            # Standard fields
            amount = st.number_input(
                "Amount ($)", 
                value=float(template.get('default_amount', 0.0)), 
                step=0.01, 
                key=f"{form_key}_amount"
            )
            transaction_date = st.date_input("Date", value=date.today(), key=f"{form_key}_date")
            payment_method = st.selectbox(
                "Payment Method", 
                ["Bank Transfer", "Credit Card", "Cash", "Cheque", "Direct Deposit"],
                index=0 if template.get('default_payment_method') == 'Bank Transfer' else 0,
                key=f"{form_key}_payment"
            )
            
            # Custom fields from schema
            custom_data = {}
            fields_schema = template.get('fields_schema', {})
            
            if fields_schema:
                st.markdown("---")
                st.markdown("**Additional Details**")
                
                for field_name, field_config in fields_schema.items():
                    field_type = field_config.get('type', 'text')
                    field_label = field_config.get('label', field_name.replace('_', ' ').title())
                    required = field_config.get('required', False)
                    
                    if field_type == 'text':
                        custom_data[field_name] = st.text_input(
                            field_label + (" *" if required else ""),
                            key=f"{form_key}_{field_name}"
                        )
                    elif field_type == 'number':
                        custom_data[field_name] = st.number_input(
                            field_label + (" *" if required else ""),
                            value=field_config.get('default', 0.0),
                            key=f"{form_key}_{field_name}"
                        )
                    elif field_type == 'select':
                        options = field_config.get('options', [])
                        custom_data[field_name] = st.selectbox(
                            field_label + (" *" if required else ""),
                            options,
                            key=f"{form_key}_{field_name}"
                        )
                    elif field_type == 'date':
                        custom_data[field_name] = st.date_input(
                            field_label + (" *" if required else ""),
                            key=f"{form_key}_{field_name}"
                        ).strftime('%Y-%m-%d')
            
            notes = st.text_input("Notes (optional)", placeholder="Add details here...", key=f"{form_key}_notes")
            
            # Action buttons
            col_cancel, col_add = st.columns(2)
            with col_cancel:
                if st.button("Cancel", key=f"{form_key}_cancel"):
                    st.session_state[f"show_{form_key}_form"] = False
                    st.rerun()
            with col_add:
                if st.button("Add", type="primary", key=f"{form_key}_add"):
                    # Validate required custom fields
                    validation_errors = []
                    for field_name, field_config in fields_schema.items():
                        if field_config.get('required') and not custom_data.get(field_name):
                            validation_errors.append(f"{field_config.get('label', field_name)} is required")
                    
                    if validation_errors:
                        st.session_state['flash_error'] = "❌ " + ", ".join(validation_errors)
                        st.rerun()
                        return
                    
                    try:
                        # Build transaction
                        transaction = {
                            'date': transaction_date.strftime('%Y-%m-%d'),
                            'amount': float(amount),
                            'type': template['transaction_type'],
                            'description': template['template_name'] + (f" - {notes}" if notes else ""),
                            'category': template['category'],
                            'payment_method': payment_method
                        }
                        
                        # Add custom fields to transaction
                        if custom_data:
                            # Store custom fields in additional_data (already handled by DatabaseService)
                            transaction.update(custom_data)
                        
                        # Save transaction
                        current_user = AuthMiddleware.get_current_user_id()
                        user_id = str(current_user.get("user_id") if isinstance(current_user, dict) else current_user or "default_user")
                        transaction_id = DatabaseService.add_transaction(transaction, user_id)
                        
                        st.session_state['flash_success'] = f"✅ {template['template_name']} added: ${amount:.2f}"
                        st.session_state[f"show_{form_key}_form"] = False
                    except Exception as e:
                        st.session_state['flash_error'] = f"❌ Failed to add transaction: {str(e)}"
                    
                    st.rerun()
