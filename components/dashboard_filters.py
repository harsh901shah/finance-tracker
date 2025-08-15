import streamlit as st

def render_dashboard_filters():
    """Render dashboard filters in a consistent row layout"""
    
    # Load CSS
    with open('styles/dashboard.css') as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)
    
    # Filter row using Streamlit columns (no custom HTML wrappers)
    col1, col2, col3, col4, col5 = st.columns([2, 2, 2, 2, 1])
    
    with col1:
        period = st.selectbox("Period", ["This Month", "Last Month", "Last 3 Months", "This Year"])
    
    with col2:
        transaction_type = st.multiselect("Transaction Type", ["Income", "Expense", "Investment", "Transfer"])
    
    with col3:
        category = st.multiselect("Category", ["Food", "Transportation", "Housing", "Utilities", "Entertainment"])
    
    with col4:
        payment_method = st.multiselect("Payment Method", ["Cash", "Credit Card", "Debit Card", "Bank Transfer"])
    
    with col5:
        apply_filters = st.button("Apply Filters", use_container_width=True)
    
    return {
        'period': period,
        'transaction_type': transaction_type,
        'category': category,
        'payment_method': payment_method,
        'apply_filters': apply_filters
    }

def render_kpi_card(kpi):
    """Render a single KPI card as complete HTML"""
    delta_html = ""
    if kpi.get('delta') is not None:
        delta_color = {
            'positive': '#00D924',
            'negative': '#FF3B30', 
            'neutral': '#8E8E93'
        }[kpi.get('delta_type', 'neutral')]
        
        delta_icon = '↗' if kpi.get('delta_type') == 'positive' else '↘' if kpi.get('delta_type') == 'negative' else '→'
        delta_html = f'<div class="kpi-delta" style="background-color: {delta_color}15; color: {delta_color};">{delta_icon} {abs(kpi["delta"]):.1f}%</div>'
    
    caption_text = "vs last period" if kpi.get('delta') is not None else ""
    
    return f'''<div class="kpi-card">
        <div class="kpi-header">
            <div class="kpi-icon">{kpi.get('icon', '📊')}</div>
            <div class="kpi-title">{kpi.get('title', 'N/A')}</div>
        </div>
        <div class="kpi-value">{kpi.get('value', '0')}</div>
        {delta_html}
        <div class="kpi-caption">{caption_text}</div>
    </div>'''

def render_kpi_grid(kpis):
    """Render KPI cards as a single HTML block to prevent ghost containers"""
    cards_html = ''.join([render_kpi_card(kpi) for kpi in kpis])
    
    css_and_html = f'''<style>
#kpi-section .kpi-grid {{
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 16px;
    margin: 16px 0;
}}
@media (max-width: 1024px) {{
    #kpi-section .kpi-grid {{ grid-template-columns: repeat(2, 1fr); }}
}}
@media (max-width: 640px) {{
    #kpi-section .kpi-grid {{ grid-template-columns: 1fr; }}
}}
#kpi-section .kpi-card {{
    background: #fff;
    border: 1px solid #e5e7eb;
    border-radius: 12px;
    padding: 16px;
    min-height: 140px;
    box-shadow: 0 1px 3px rgba(0,0,0,0.04);
}}
</style>
<section id="kpi-section"><div class="kpi-grid">{cards_html}</div></section>'''
    
    st.markdown(css_and_html, unsafe_allow_html=True)