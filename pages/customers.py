import streamlit as st
import pandas as pd
from datetime import datetime

st.title("👥 Customer Management")

# Get data
sales_df = st.session_state.data_manager.get_sales()
repairs_df = st.session_state.data_manager.get_repairs()

# Search bar for customers
st.header("🔍 Find Customer")
search_term = st.text_input("Search by name or phone number")

# Combine and process customer data
def get_customer_history(name=None, phone=None):
    # Get all repairs for the customer
    customer_repairs = repairs_df[
        (repairs_df['customer_name'].str.contains(name, case=False, na=False) if name else True) |
        (repairs_df['phone'].str.contains(phone, case=False, na=False) if phone else True)
    ].copy()
    
    # Get all sales for the customer
    customer_sales = sales_df[
        (sales_df['customer_name'].str.contains(name, case=False, na=False) if name else True) |
        (sales_df['phone'].str.contains(phone, case=False, na=False) if phone else True)
    ].copy()
    
    return customer_repairs, customer_sales

if search_term:
    customer_repairs, customer_sales = get_customer_history(search_term, search_term)
    
    if not customer_repairs.empty or not customer_sales.empty:
        # Get unique customers from both datasets
        unique_customers = pd.concat([
            customer_repairs[['customer_name', 'phone']],
            customer_sales[['customer_name', 'phone']]
        ]).drop_duplicates()
        
        for _, customer in unique_customers.iterrows():
            with st.expander(f"📋 {customer['customer_name']} - {customer['phone']}"):
                # Customer Statistics
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    total_repairs = len(customer_repairs[
                        (customer_repairs['customer_name'] == customer['customer_name']) &
                        (customer_repairs['phone'] == customer['phone'])
                    ])
                    st.metric("Total Repairs", total_repairs)
                
                with col2:
                    total_sales = len(customer_sales[
                        (customer_sales['customer_name'] == customer['customer_name']) &
                        (customer_sales['phone'] == customer['phone'])
                    ])
                    st.metric("Total Purchases", total_sales)
                
                with col3:
                    total_spent = customer_sales[
                        (customer_sales['customer_name'] == customer['customer_name']) &
                        (customer_sales['phone'] == customer['phone'])
                    ]['price'].sum()
                    st.metric("Total Spent", f"${total_spent:.2f}")
                
                # Repair History
                st.subheader("🔧 Repair History")
                customer_repair_history = customer_repairs[
                    (customer_repairs['customer_name'] == customer['customer_name']) &
                    (customer_repairs['phone'] == customer['phone'])
                ].sort_values('date', ascending=False)
                
                if not customer_repair_history.empty:
                    for _, repair in customer_repair_history.iterrows():
                        status_color = {
                            "Pending": "🟡",
                            "In Progress": "🔵",
                            "Waiting for Parts": "🔴",
                            "Ready for Pickup": "🟢",
                            "Completed": "⚪"
                        }.get(repair['status'], "⚪")
                        
                        st.markdown(f"""
                        {status_color} **{repair['device']}** - {repair['date']}
                        - Issue: {repair['issue']}
                        - Status: {repair['status']}
                        - Cost: ${float(repair['estimated_cost']):.2f}
                        """)
                else:
                    st.info("No repair history found")
                
                # Purchase History
                st.subheader("🛍️ Purchase History")
                customer_purchase_history = customer_sales[
                    (customer_sales['customer_name'] == customer['customer_name']) &
                    (customer_sales['phone'] == customer['phone'])
                ].sort_values('date', ascending=False)
                
                if not customer_purchase_history.empty:
                    for _, sale in customer_purchase_history.iterrows():
                        st.markdown(f"""
                        🏷️ **{sale['item']}** - {sale['date']}
                        - Price: ${float(sale['price']):.2f}
                        - Payment: {sale['payment_method']}
                        """)
                else:
                    st.info("No purchase history found")
                
                # Display customer photo if available
                if 'photo_path' in customer_repair_history.columns:
                    latest_photo = customer_repair_history.iloc[0]['photo_path'] if not customer_repair_history.empty else None
                    if latest_photo and pd.notna(latest_photo):
                        photo_data = st.session_state.data_manager.get_photo_as_base64(latest_photo)
                        if photo_data:
                            st.markdown("📸 **Customer Photo**")
                            st.markdown(f"""
                                <img src="data:image/jpeg;base64,{photo_data}"
                                    style="width: 150px; border-radius: 10px; margin: 10px 0;"
                                />
                            """, unsafe_allow_html=True)
    else:
        st.warning("No customers found matching your search")
else:
    # Show recent customers
    st.subheader("Recent Customers")
    recent_repairs = repairs_df.sort_values('date', ascending=False).head(5)
    recent_sales = sales_df.sort_values('date', ascending=False).head(5)
    
    recent_customers = pd.concat([
        recent_repairs[['customer_name', 'phone', 'date']],
        recent_sales[['customer_name', 'phone', 'date']]
    ]).drop_duplicates().sort_values('date', ascending=False).head(5)
    
    for _, customer in recent_customers.iterrows():
        st.markdown(f"👤 **{customer['customer_name']}** - {customer['phone']}")
