import streamlit as st
from utils.data_manager import DataManager
from datetime import datetime

st.set_page_config(
    page_title="GSM-Lab Management System",
    page_icon="📱",
    layout="wide"
)

# Initialize data manager
if 'data_manager' not in st.session_state:
    st.session_state.data_manager = DataManager()

# Main page header
st.title("📱 GSM-Lab Management System")

# Dashboard overview
st.header("Dashboard Overview")

# Create three columns for key metrics
col1, col2, col3 = st.columns(3)

# Get data for metrics
sales_df = st.session_state.data_manager.get_sales()
repairs_df = st.session_state.data_manager.get_repairs()
inventory_df = st.session_state.data_manager.get_inventory()

with col1:
    st.metric(
        label="Today's Sales",
        value=f"${sales_df[sales_df['date'].str.contains(datetime.now().strftime('%Y-%m-%d'))]['price'].sum():.2f}"
    )

with col2:
    st.metric(
        label="Active Repairs",
        value=len(repairs_df[repairs_df['status'] != 'Completed'])
    )

with col3:
    st.metric(
        label="Low Stock Items",
        value=len(inventory_df[inventory_df['quantity'] <= inventory_df['threshold']])
    )

# Quick Links
st.header("Quick Links")
st.write("""
- **Sales**: Record new sales and view sales history
- **Repairs**: Manage repair tickets and track progress
- **Inventory**: Monitor parts and stock levels
- **Reports**: View business analytics and reports
""")

# Footer
st.markdown("---")
st.markdown("### GSM-Lab Management System v1.0")
st.markdown("For support, contact system administrator")