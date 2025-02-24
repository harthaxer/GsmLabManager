import streamlit as st
import pandas as pd
from datetime import datetime

st.title("🔧 Repair Management")

# Define repair categories with colors
REPAIR_CATEGORIES = {
    "Screen Repair": {"color": "#FF4B4B", "icon": "📱"},
    "Battery Replacement": {"color": "#4BB543", "icon": "🔋"},
    "Water Damage": {"color": "#1E90FF", "icon": "💧"},
    "Charging Port": {"color": "#FFA500", "icon": "⚡"},
    "Speaker/Audio": {"color": "#9370DB", "icon": "🔊"},
    "Camera Issue": {"color": "#20B2AA", "icon": "📸"},
    "Other": {"color": "#808080", "icon": "🔨"}
}

tab1, tab2 = st.tabs(["New Repair", "Active Repairs"])

with tab1:
    st.header("Create New Repair Ticket")

    with st.form("repair_form"):
        # Customer Information
        st.subheader("📋 Customer Information")
        col1, col2 = st.columns(2)
        with col1:
            customer_name = st.text_input("Customer Name")
        with col2:
            phone = st.text_input("Phone Number")

        # Device Information
        st.subheader("📱 Device Information")
        col1, col2 = st.columns(2)
        with col1:
            device = st.text_input("Device Model")
        with col2:
            repair_category = st.selectbox(
                "Repair Category",
                options=list(REPAIR_CATEGORIES.keys()),
                format_func=lambda x: f"{REPAIR_CATEGORIES[x]['icon']} {x}"
            )

        # Issue Description
        st.subheader("🔍 Issue Details")
        issue = st.text_area("Issue Description")

        # Cost Estimation
        st.subheader("💰 Cost Estimation")
        estimated_cost = st.number_input("Estimated Cost", min_value=0.0, format="%.2f")

        # Submit button with custom styling
        submit_button = st.form_submit_button(
            "Create Repair Ticket",
            use_container_width=True
        )

        if submit_button:
            if customer_name and phone and device and issue:
                repair_data = {
                    'customer_name': customer_name,
                    'phone': phone,
                    'device': device,
                    'category': repair_category,
                    'issue': issue,
                    'estimated_cost': estimated_cost,
                    'status': 'Pending',
                    'completion_date': None
                }
                st.session_state.data_manager.add_repair(repair_data)
                st.success("✅ Repair ticket created successfully!")
            else:
                st.error("❌ Please fill all required fields!")

with tab2:
    st.header("Active Repairs")

    repairs_df = st.session_state.data_manager.get_repairs()

    # Filter for active repairs
    active_repairs = repairs_df[repairs_df['status'] != 'Completed'].copy()

    # Status colors
    STATUS_COLORS = {
        "Pending": "#FFA500",
        "In Progress": "#1E90FF",
        "Waiting for Parts": "#FF4B4B",
        "Ready for Pickup": "#4BB543",
        "Completed": "#808080"
    }

    if not active_repairs.empty:
        for idx, repair in active_repairs.iterrows():
            # Create a colored container for each repair ticket
            with st.container():
                # Get category with fallback to 'Other' if not present
                category = 'Other'
                if 'category' in repair and pd.notna(repair['category']):
                    category = repair['category']

                accent_color = REPAIR_CATEGORIES[category]['color']
                category_icon = REPAIR_CATEGORIES[category]['icon']

                st.markdown(
                    f"""
                    <div style="
                        border-left: 5px solid {accent_color};
                        padding: 10px;
                        margin: 10px 0;
                        background-color: #F0F2F6;
                        border-radius: 5px;
                    ">
                        <h3>{category_icon} {repair['customer_name']} - {repair['device']}</h3>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

                # Edit mode toggle
                edit_mode = st.toggle("Edit Ticket", key=f"edit_{idx}")

                if edit_mode:
                    # Edit form
                    with st.form(key=f"edit_form_{idx}"):
                        col1, col2 = st.columns(2)
                        with col1:
                            updated_name = st.text_input("Customer Name", repair['customer_name'])
                            updated_phone = st.text_input("Phone", repair['phone'])
                            updated_device = st.text_input("Device", repair['device'])
                        with col2:
                            updated_category = st.selectbox(
                                "Category",
                                options=list(REPAIR_CATEGORIES.keys()),
                                index=list(REPAIR_CATEGORIES.keys()).index(category),
                                key=f"cat_{idx}"
                            )
                            updated_status = st.selectbox(
                                "Status",
                                ["Pending", "In Progress", "Waiting for Parts", "Ready for Pickup", "Completed"],
                                index=["Pending", "In Progress", "Waiting for Parts", "Ready for Pickup", "Completed"].index(repair['status']),
                                key=f"status_{idx}"
                            )

                        updated_issue = st.text_area("Issue Description", repair['issue'])
                        updated_cost = st.number_input("Estimated Cost", min_value=0.0, value=float(repair['estimated_cost']), format="%.2f")

                        if st.form_submit_button("Save Changes"):
                            # Update the repair in the DataFrame
                            repairs_df.loc[idx, 'customer_name'] = updated_name
                            repairs_df.loc[idx, 'phone'] = updated_phone
                            repairs_df.loc[idx, 'device'] = updated_device
                            repairs_df.loc[idx, 'category'] = updated_category
                            repairs_df.loc[idx, 'issue'] = updated_issue
                            repairs_df.loc[idx, 'estimated_cost'] = updated_cost
                            repairs_df.loc[idx, 'status'] = updated_status

                            if updated_status == "Completed" and repair['status'] != "Completed":
                                repairs_df.loc[idx, 'completion_date'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

                            # Save the updated DataFrame
                            repairs_df.to_csv(f"{st.session_state.data_manager.data_dir}/repairs.csv", index=False)
                            st.success("✅ Repair ticket updated successfully!")
                            st.rerun()
                else:
                    # Display mode
                    col1, col2 = st.columns([2, 1])
                    with col1:
                        st.write(f"**📱 Device:** {repair['device']}")
                        st.write(f"**📞 Phone:** {repair['phone']}")
                        st.write(f"**💬 Issue:** {repair['issue']}")
                        st.write(f"**💰 Estimated Cost:** ${repair['estimated_cost']:.2f}")

                    with col2:
                        current_status = repair['status']
                        st.markdown(f"""
                            <div style="
                                padding: 5px 10px;
                                background-color: {STATUS_COLORS[current_status]};
                                color: white;
                                border-radius: 15px;
                                text-align: center;
                                margin: 5px 0;
                            ">
                                {current_status}
                            </div>
                        """, unsafe_allow_html=True)
    else:
        st.info("No active repairs at the moment.")