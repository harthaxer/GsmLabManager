import streamlit as st
import pandas as pd
from datetime import datetime

st.title("Repair Management")

tab1, tab2 = st.tabs(["New Repair", "Active Repairs"])

with tab1:
    st.header("Create New Repair Ticket")
    
    with st.form("repair_form"):
        customer_name = st.text_input("Customer Name")
        phone = st.text_input("Phone Number")
        device = st.text_input("Device Model")
        issue = st.text_area("Issue Description")
        estimated_cost = st.number_input("Estimated Cost", min_value=0.0, format="%.2f")
        
        submit_button = st.form_submit_button("Create Repair Ticket")
        
        if submit_button:
            if customer_name and phone and device and issue:
                repair_data = {
                    'customer_name': customer_name,
                    'phone': phone,
                    'device': device,
                    'issue': issue,
                    'estimated_cost': estimated_cost,
                    'status': 'Pending',
                    'completion_date': None
                }
                st.session_state.data_manager.add_repair(repair_data)
                st.success("Repair ticket created successfully!")
            else:
                st.error("Please fill all required fields!")

with tab2:
    st.header("Active Repairs")
    
    repairs_df = st.session_state.data_manager.get_repairs()
    
    # Filter for active repairs
    active_repairs = repairs_df[repairs_df['status'] != 'Completed'].copy()
    
    for idx, repair in active_repairs.iterrows():
        with st.expander(f"{repair['customer_name']} - {repair['device']}"):
            st.write(f"**Phone:** {repair['phone']}")
            st.write(f"**Issue:** {repair['issue']}")
            st.write(f"**Estimated Cost:** ${repair['estimated_cost']:.2f}")
            st.write(f"**Current Status:** {repair['status']}")
            
            new_status = st.selectbox(
                "Update Status",
                ["Pending", "In Progress", "Waiting for Parts", "Ready for Pickup", "Completed"],
                key=f"status_{idx}"
            )
            
            if st.button("Update Status", key=f"update_{idx}"):
                st.session_state.data_manager.update_repair_status(idx, new_status)
                st.success("Status updated successfully!")
                st.rerun()
