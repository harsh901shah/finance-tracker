import streamlit as st

def render_dashboard_filters():
    """Render dashboard filters in a consistent row layout"""
    
    # Load CSS
    with open('styles/dashboard.css') as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)
    
    # Filter row using Streamlit columns
    col1, col2, col3, col4, col5 = st.columns([2, 2, 2, 2, 1])
    
    with col1:
        period = st.selectbox("Period", ["This Month", "Last Month", "Last 3 Months", "This Year"])
    
    with col2:
        transaction_type = st.multiselect(
            "Transaction Type", 
            ["Income", "Expense", "Investment", "Transfer"],
            default=["Income", "Expense"]
        )
    
    with col3:
        category = st.selectbox("Category", ["All Categories", "Food", "Transportation", "Housing", "Utilities", "Entertainment"])
    
    with col4:
        payment_method = st.multiselect(
            "Payment Method", 
            ["Cash", "Credit Card", "Debit Card", "Bank Transfer"],
            placeholder="All Methods"
        )
    
    with col5:
        apply_filters = st.button("Apply", type="primary", use_container_width=True)
    
    return {
        'period': period,
        'transaction_type': transaction_type,
        'category': [category] if category != "All Categories" else [],
        'payment_method': payment_method,
        'apply_filters': apply_filters
    }

def render_kpi_card(kpi):
    """Render a single KPI card as complete HTML"""
    delta_html = ""
    if kpi.get('delta') is not None and kpi.get('delta') != 0:
        delta_color = {
            'positive': '#00D924',
            'negative': '#FF3B30', 
            'neutral': '#8E8E93'
        }[kpi.get('delta_type', 'neutral')]
        
        delta_icon = '↗' if kpi.get('delta_type') == 'positive' else '↘' if kpi.get('delta_type') == 'negative' else '→'
        delta_html = f'<div class="kpi-delta" style="background-color: {delta_color}15; color: {delta_color};">{delta_icon} {abs(kpi["delta"]):.1f}%</div>'
    
    caption_text = "vs last period" if delta_html else "Current period"
    
    return f'''<div class="kpi-card">
        <div class="kpi-header">
            <div class="kpi-icon">{kpi.get('icon', '📊')}</div>
            <div class="kpi-title">{kpi.get('title', 'N/A')}</div>
        </div>
        <div class="kpi-value">{kpi.get('value', '$0')}</div>
        {delta_html}
        <div class="kpi-caption">{caption_text}</div>
    </div>'''

def render_kpi_grid(kpis):
    """Render KPI cards using native Streamlit components"""
    cols = st.columns(len(kpis))
    
    for i, kpi in enumerate(kpis):
        with cols[i]:
            # Create delta string
            delta_str = None
            if kpi.get('delta') is not None and kpi.get('delta') != 0:
                delta_str = f"{kpi['delta']:.1f}%"
            
            # Display metric
            st.metric(
                label=f"{kpi.get('icon', '📊')} {kpi.get('title', 'N/A')}",
                value=kpi.get('value', '$0'),
                delta=delta_str
            )