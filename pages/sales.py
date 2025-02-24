import streamlit as st
import pandas as pd
from datetime import datetime

st.title("Sales Management")

tab1, tab2 = st.tabs(["New Sale", "Sales History"])

with tab1:
    st.header("Record New Sale")
    
    with st.form("sale_form"):
        customer_name = st.text_input("Customer Name")
        phone = st.text_input("Phone Number")
        item = st.text_input("Item Sold")
        price = st.number_input("Price", min_value=0.0, format="%.2f")
        payment_method = st.selectbox("Payment Method", ["Cash", "Card", "Mobile Payment"])
        
        submit_button = st.form_submit_button("Record Sale")
        
        if submit_button:
            if customer_name and phone and item and price > 0:
                sale_data = {
                    'customer_name': customer_name,
                    'phone': phone,
                    'item': item,
                    'price': price,
                    'payment_method': payment_method
                }
                st.session_state.data_manager.add_sale(sale_data)
                st.success("Sale recorded successfully!")
            else:
                st.error("Please fill all required fields!")

with tab2:
    st.header("Sales History")
    
    # Filters
    col1, col2 = st.columns(2)
    with col1:
        date_filter = st.date_input("Filter by Date")
    with col2:
        payment_filter = st.multiselect("Payment Method", ["Cash", "Card", "Mobile Payment"])
    
    sales_df = st.session_state.data_manager.get_sales()
    
    # Apply filters
    if date_filter:
        sales_df = sales_df[sales_df['date'].str.contains(date_filter.strftime('%Y-%m-%d'))]
    if payment_filter:
        sales_df = sales_df[sales_df['payment_method'].isin(payment_filter)]
    
    st.dataframe(sales_df)
    
    # Summary statistics
    st.subheader("Summary")
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Total Sales", f"${sales_df['price'].sum():.2f}")
    with col2:
        st.metric("Number of Transactions", len(sales_df))
