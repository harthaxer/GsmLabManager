import streamlit as st
import pandas as pd
from datetime import datetime
import os

# Set page configuration for better layout
st.set_page_config(layout="wide")

# Custom CSS for better styling
st.markdown("""
<style>
    .repair-card {
        border: 1px solid #e6e6e6;
        border-radius: 10px;
        padding: 20px;
        margin: 10px 0;
        background-color: white;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .status-badge {
        padding: 5px 15px;
        border-radius: 15px;
        color: white;
        display: inline-block;
        font-weight: bold;
    }
    .category-icon {
        font-size: 24px;
        margin-right: 10px;
    }
    .stat-card {
        background-color: white;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        text-align: center;
    }
</style>
""", unsafe_allow_html=True)

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

# Get data
repairs_df = st.session_state.data_manager.get_repairs()

# Dashboard Stats
st.header("📊 Dashboard Overview")
col1, col2, col3, col4 = st.columns(4)

active_repairs = repairs_df[repairs_df['status'] != 'Completed']
with col1:
    st.markdown("""
        <div class="stat-card">
            <h3>Active Repairs</h3>
            <h2>%d</h2>
        </div>
    """ % len(active_repairs), unsafe_allow_html=True)

with col2:
    pending_repairs = len(repairs_df[repairs_df['status'] == 'Pending'])
    st.markdown("""
        <div class="stat-card">
            <h3>Pending</h3>
            <h2>%d</h2>
        </div>
    """ % pending_repairs, unsafe_allow_html=True)

with col3:
    in_progress = len(repairs_df[repairs_df['status'] == 'In Progress'])
    st.markdown("""
        <div class="stat-card">
            <h3>In Progress</h3>
            <h2>%d</h2>
        </div>
    """ % in_progress, unsafe_allow_html=True)

with col4:
    ready_pickup = len(repairs_df[repairs_df['status'] == 'Ready for Pickup'])
    st.markdown("""
        <div class="stat-card">
            <h3>Ready for Pickup</h3>
            <h2>%d</h2>
        </div>
    """ % ready_pickup, unsafe_allow_html=True)

# Main content tabs
tab1, tab2 = st.tabs(["📝 New Repair", "🔄 Active Repairs"])

with tab1:
    st.header("Create New Repair Ticket")

    with st.form("repair_form", clear_on_submit=True):
        # Customer Information Section
        st.markdown("""
            <div style="background-color: #f8f9fa; padding: 20px; border-radius: 10px; margin: 10px 0;">
                <h3>👤 Customer Information</h3>
            </div>
        """, unsafe_allow_html=True)

        col1, col2 = st.columns(2)
        with col1:
            customer_name = st.text_input("Customer Name")
            phone = st.text_input("Phone Number")
        with col2:
            camera_photo = st.camera_input("Take Customer Photo")

        # Device Information Section
        st.markdown("""
            <div style="background-color: #f8f9fa; padding: 20px; border-radius: 10px; margin: 10px 0;">
                <h3>📱 Device Information</h3>
            </div>
        """, unsafe_allow_html=True)

        col1, col2 = st.columns(2)
        with col1:
            device = st.text_input("Device Model")
        with col2:
            repair_category = st.selectbox(
                "Repair Category",
                options=list(REPAIR_CATEGORIES.keys()),
                format_func=lambda x: f"{REPAIR_CATEGORIES[x]['icon']} {x}"
            )

        # Issue Details Section
        st.markdown("""
            <div style="background-color: #f8f9fa; padding: 20px; border-radius: 10px; margin: 10px 0;">
                <h3>🔍 Issue Details</h3>
            </div>
        """, unsafe_allow_html=True)

        issue = st.text_area("Issue Description")
        estimated_cost = st.number_input("Estimated Cost", min_value=0.0, format="%.2f")

        # Submit button with custom styling
        submit = st.form_submit_button("Create Repair Ticket", use_container_width=True)

        if submit:
            if customer_name and phone and device and issue:
                # Process photo if available
                photo_path = None
                if camera_photo:
                    photo_path = st.session_state.data_manager.save_customer_photo(
                        camera_photo.getvalue(),
                        customer_name
                    )

                repair_data = {
                    'customer_name': customer_name,
                    'phone': phone,
                    'device': device,
                    'category': repair_category,
                    'issue': issue,
                    'estimated_cost': estimated_cost,
                    'status': 'Pending',
                    'completion_date': None,
                    'photo_path': photo_path
                }
                st.session_state.data_manager.add_repair(repair_data)
                st.success("✅ Repair ticket created successfully!")
            else:
                st.error("❌ Please fill all required fields!")

with tab2:
    # Filter controls in an expanded section
    with st.expander("🔍 Filter Options", expanded=True):
        col1, col2, col3 = st.columns(3)
        with col1:
            status_filter = st.multiselect(
                "Status",
                ["Pending", "In Progress", "Waiting for Parts", "Ready for Pickup"],
                default=["Pending", "In Progress", "Waiting for Parts", "Ready for Pickup"]
            )
        with col2:
            category_filter = st.multiselect(
                "Category",
                list(REPAIR_CATEGORIES.keys()),
                default=list(REPAIR_CATEGORIES.keys())
            )
        with col3:
            search_term = st.text_input("Search by name or device")

    # Filter the dataframe
    active_repairs = repairs_df[
        (repairs_df['status'].isin(status_filter)) &
        (repairs_df['status'] != 'Completed')
    ].copy()

    if category_filter:
        active_repairs = active_repairs[active_repairs['category'].isin(category_filter)]

    if search_term:
        mask = (
            active_repairs['customer_name'].str.contains(search_term, case=False, na=False) |
            active_repairs['device'].str.contains(search_term, case=False, na=False)
        )
        active_repairs = active_repairs[mask]

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
            # Get category with fallback to 'Other'
            category = 'Other'
            if 'category' in repair and pd.notna(repair['category']):
                category = repair['category']

            # Create repair card
            st.markdown(f"""
                <div class="repair-card">
                    <div style="border-left: 5px solid {REPAIR_CATEGORIES[category]['color']}; padding-left: 15px;">
                        <span class="category-icon">{REPAIR_CATEGORIES[category]['icon']}</span>
                        <span style="font-size: 1.2em; font-weight: bold;">{repair['customer_name']} - {repair['device']}</span>
                    </div>
                """, unsafe_allow_html=True)

            col1, col2 = st.columns([1, 3])

            with col1:
                # Display customer photo
                if 'photo_path' in repair and pd.notna(repair['photo_path']):
                    photo_data = st.session_state.data_manager.get_photo_as_base64(repair['photo_path'])
                    if photo_data:
                        st.markdown(f"""
                            <img src="data:image/jpeg;base64,{photo_data}"
                                style="width: 150px; border-radius: 10px; margin: 10px 0;"
                            />
                        """, unsafe_allow_html=True)
                else:
                    st.image("https://via.placeholder.com/150?text=No+Photo", width=150)

            with col2:
                # Edit mode toggle
                edit_mode = st.toggle("✏️ Edit Ticket", key=f"edit_{idx}")

                if edit_mode:
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

                        new_photo = st.camera_input("Update Photo")
                        updated_issue = st.text_area("Issue Description", repair['issue'])
                        updated_cost = st.number_input("Cost", min_value=0.0, value=float(repair['estimated_cost']), format="%.2f")

                        col1, col2 = st.columns(2)
                        with col1:
                            save = st.form_submit_button("💾 Save Changes")

                        if save:
                            # Process new photo if taken
                            photo_path = repair['photo_path']
                            if new_photo:
                                photo_path = st.session_state.data_manager.save_customer_photo(
                                    new_photo.getvalue(),
                                    updated_name
                                )

                            # Update repairs DataFrame
                            repairs_df.loc[idx, 'customer_name'] = updated_name
                            repairs_df.loc[idx, 'phone'] = updated_phone
                            repairs_df.loc[idx, 'device'] = updated_device
                            repairs_df.loc[idx, 'category'] = updated_category
                            repairs_df.loc[idx, 'issue'] = updated_issue
                            repairs_df.loc[idx, 'estimated_cost'] = updated_cost
                            repairs_df.loc[idx, 'status'] = updated_status
                            repairs_df.loc[idx, 'photo_path'] = photo_path

                            if updated_status == "Completed" and repair['status'] != "Completed":
                                repairs_df.loc[idx, 'completion_date'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

                            repairs_df.to_csv(f"{st.session_state.data_manager.data_dir}/repairs.csv", index=False)
                            st.success("✅ Changes saved successfully!")
                            st.rerun()
                else:
                    # Display mode with improved layout
                    col1, col2 = st.columns([2, 1])
                    with col1:
                        st.markdown(f"""
                            <div style="background-color: #f8f9fa; padding: 15px; border-radius: 8px;">
                                <p><strong>📞 Phone:</strong> {repair['phone']}</p>
                                <p><strong>💬 Issue:</strong> {repair['issue']}</p>
                                <p><strong>💰 Cost:</strong> ${repair['estimated_cost']:.2f}</p>
                            </div>
                        """, unsafe_allow_html=True)

                    with col2:
                        st.markdown(f"""
                            <div style="text-align: center;">
                                <div class="status-badge" style="background-color: {STATUS_COLORS[repair['status']]};">
                                    {repair['status']}
                                </div>
                            </div>
                        """, unsafe_allow_html=True)

            st.markdown("</div>", unsafe_allow_html=True)
    else:
        st.info("🔍 No active repairs match your filters.")