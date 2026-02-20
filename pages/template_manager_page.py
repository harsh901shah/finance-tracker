import streamlit as st
import json
from services.template_service import TemplateService
from utils.auth_middleware import AuthMiddleware

class TemplateManagerPage:
    """Page for managing transaction templates"""
    
    @staticmethod
    def show():
        st.header("⚙️ Manage Transaction Templates")
        st.markdown("Create custom transaction types with your own fields and categories.")
        
        # Get current user
        current_user = AuthMiddleware.get_current_user_id()
        if not current_user:
            st.error("🔒 Please login to manage templates")
            return
        user_id = str(current_user.get('user_id') if isinstance(current_user, dict) else current_user)
        
        # Initialize templates table
        try:
            TemplateService.initialize_templates_table()
        except Exception as e:
            st.error(f"Failed to initialize templates: {e}")
            return
        
        # Tabs for different actions
        tab1, tab2 = st.tabs(["📋 My Templates", "➕ Create New"])
        
        with tab1:
            TemplateManagerPage._show_templates_list(user_id)
        
        with tab2:
            TemplateManagerPage._show_create_form(user_id)
    
    @staticmethod
    def _show_templates_list(user_id: str):
        """Display list of user's templates"""
        templates = TemplateService.get_user_templates(user_id, active_only=False)
        
        if not templates:
            st.info("No templates yet. Create your first custom transaction type!")
            if st.button("🌱 Seed Default Templates"):
                TemplateService.seed_default_templates(user_id)
                st.success("✅ Default templates added!")
                st.rerun()
            return
        
        st.subheader(f"📊 {len(templates)} Templates")
        
        for template in templates:
            with st.expander(f"{template['icon']} {template['template_name']}", expanded=False):
                col1, col2 = st.columns([3, 1])
                
                with col1:
                    st.markdown(f"**Type:** {template['transaction_type']}")
                    st.markdown(f"**Category:** {template['category']}")
                    st.markdown(f"**Default Amount:** ${template['default_amount']:.2f}")
                    st.markdown(f"**Payment Method:** {template['default_payment_method']}")
                    st.markdown(f"**Status:** {'✅ Active' if template['is_active'] else '❌ Inactive'}")
                    
                    if template.get('fields_schema'):
                        st.markdown("**Custom Fields:**")
                        for field_name, field_config in template['fields_schema'].items():
                            st.markdown(f"- {field_config.get('label', field_name)} ({field_config.get('type', 'text')})")
                
                with col2:
                    if template['is_active']:
                        if st.button("🚫 Deactivate", key=f"deactivate_{template['id']}"):
                            TemplateService.update_template(template['id'], user_id, {'is_active': 0})
                            st.success("Template deactivated")
                            st.rerun()
                    else:
                        if st.button("✅ Activate", key=f"activate_{template['id']}"):
                            TemplateService.update_template(template['id'], user_id, {'is_active': 1})
                            st.success("Template activated")
                            st.rerun()
                    
                    if st.button("🗑️ Delete", key=f"delete_{template['id']}"):
                        TemplateService.delete_template(template['id'], user_id)
                        st.success("Template deleted")
                        st.rerun()
    
    @staticmethod
    def _show_create_form(user_id: str):
        """Show form to create new template"""
        st.subheader("Create Custom Transaction Template")
        
        with st.form("create_template", clear_on_submit=False):
            col1, col2 = st.columns(2)
            
            with col1:
                template_name = st.text_input("Template Name *", placeholder="e.g., Crypto Trading")
                icon = st.text_input("Icon", value="💰", help="Emoji icon for this template")
                transaction_type = st.selectbox("Transaction Type *", ["Income", "Expense", "Investment", "Transfer", "Tax"])
                category = st.text_input("Category *", placeholder="e.g., Cryptocurrency")
            
            with col2:
                default_amount = st.number_input("Default Amount", value=0.0, step=0.01)
                default_payment_method = st.selectbox(
                    "Default Payment Method",
                    ["Bank Transfer", "Credit Card", "Cash", "Cheque", "Direct Deposit"]
                )
                sort_order = st.number_input("Sort Order", value=100, step=1, help="Lower numbers appear first")
            
            st.markdown("---")
            st.markdown("### Custom Fields (Optional)")
            st.markdown("Add custom fields to track additional information")
            
            # Simple custom fields builder
            num_fields = st.number_input("Number of custom fields", min_value=0, max_value=10, value=0, step=1)
            
            fields_schema = {}
            for i in range(int(num_fields)):
                st.markdown(f"**Field {i+1}**")
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    field_name = st.text_input(f"Field Name", key=f"field_name_{i}", placeholder="e.g., coin_name")
                with col2:
                    field_type = st.selectbox(f"Type", ["text", "number", "select", "date"], key=f"field_type_{i}")
                with col3:
                    required = st.checkbox(f"Required", key=f"field_required_{i}")
                
                if field_name:
                    field_config = {
                        'type': field_type,
                        'label': field_name.replace('_', ' ').title(),
                        'required': required
                    }
                    
                    if field_type == 'select':
                        options_str = st.text_input(
                            f"Options (comma-separated)",
                            key=f"field_options_{i}",
                            placeholder="e.g., Bitcoin, Ethereum, Dogecoin"
                        )
                        if options_str:
                            field_config['options'] = [opt.strip() for opt in options_str.split(',')]
                    
                    fields_schema[field_name] = field_config
            
            submitted = st.form_submit_button("Create Template", type="primary", width="stretch")
            
            if submitted and template_name.strip() and category.strip():
                template_data = {
                    'template_name': template_name.strip(),
                    'icon': icon,
                    'transaction_type': transaction_type,
                    'category': category.strip(),
                    'default_amount': default_amount,
                    'default_payment_method': default_payment_method,
                    'sort_order': sort_order,
                    'fields_schema': fields_schema if fields_schema else {}
                }
                
                template_id = TemplateService.create_template(user_id, template_data)
                
                if template_id:
                    st.success(f"✅ Template '{template_name}' created successfully!")
                    st.rerun()
                else:
                    st.error("Failed to create template. It may already exist.")
        
        if submitted and (not template_name.strip() or not category.strip()):
            st.error("Template name and category are required")
