import streamlit as st
import pandas as pd
from datetime import datetime
import os

# Set page configuration for better layout
st.set_page_config(layout="wide")

# Custom CSS for better styling
st.markdown("""
<style>
    .repair-board {
        display: flex;
        overflow-x: auto;
        padding: 10px 0;
        margin: 10px 0;
    }
    .status-column {
        min-width: 300px;
        margin: 0 10px;
        padding: 15px;
        background-color: #f8f9fa;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .repair-card {
        background-color: white;
        border-radius: 8px;
        padding: 15px;
        margin: 10px 0;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        transition: transform 0.2s;
    }
    .repair-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    .status-badge {
        padding: 5px 15px;
        border-radius: 15px;
        color: white;
        display: inline-block;
        font-weight: bold;
    }
    .photo-container {
        width: 100px;
        height: 100px;
        border-radius: 50%;
        overflow: hidden;
        margin: 10px auto;
    }
    .photo-container img {
        width: 100%;
        height: 100%;
        object-fit: cover;
    }
    .category-tag {
        display: inline-block;
        padding: 3px 8px;
        border-radius: 12px;
        font-size: 0.8em;
        margin: 2px;
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

# Status configurations
STATUS_COLORS = {
    "Pending": "#FFA500",
    "In Progress": "#1E90FF",
    "Waiting for Parts": "#FF4B4B",
    "Ready for Pickup": "#4BB543",
    "Completed": "#808080"
}

# Tabs for different views
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
    # Get repairs data
    repairs_df = st.session_state.data_manager.get_repairs()

    # Filter controls
    with st.expander("🔍 Filter Options", expanded=True):
        col1, col2, col3 = st.columns(3)
        with col1:
            category_filter = st.multiselect(
                "Filter by Category",
                list(REPAIR_CATEGORIES.keys()),
                default=list(REPAIR_CATEGORIES.keys())
            )
        with col2:
            search_term = st.text_input("🔍 Search by name or device")
        with col3:
            sort_by = st.selectbox(
                "Sort by",
                ["Date (Newest)", "Date (Oldest)", "Customer Name", "Status"]
            )

    # Filter and sort repairs
    active_repairs = repairs_df[repairs_df['status'] != 'Completed'].copy()

    if category_filter:
        active_repairs = active_repairs[active_repairs['category'].isin(category_filter)]

    if search_term:
        mask = (
            active_repairs['customer_name'].str.contains(search_term, case=False, na=False) |
            active_repairs['device'].str.contains(search_term, case=False, na=False)
        )
        active_repairs = active_repairs[mask]

    # Sort repairs
    if sort_by == "Date (Newest)":
        active_repairs = active_repairs.sort_values('date', ascending=False)
    elif sort_by == "Date (Oldest)":
        active_repairs = active_repairs.sort_values('date')
    elif sort_by == "Customer Name":
        active_repairs = active_repairs.sort_values('customer_name')
    elif sort_by == "Status":
        status_order = ["Pending", "In Progress", "Waiting for Parts", "Ready for Pickup"]
        active_repairs['status_order'] = active_repairs['status'].map({s: i for i, s in enumerate(status_order)})
        active_repairs = active_repairs.sort_values('status_order')

    # Create Kanban board layout
    st.markdown("<div class='repair-board'>", unsafe_allow_html=True)

    for status in ["Pending", "In Progress", "Waiting for Parts", "Ready for Pickup"]:
        status_repairs = active_repairs[active_repairs['status'] == status]

        st.markdown(f"""
            <div class='status-column'>
                <h3>
                    {status} 
                    <span class='status-badge' style='background-color: {STATUS_COLORS[status]};'>
                        {len(status_repairs)}
                    </span>
                </h3>
        """, unsafe_allow_html=True)

        for _, repair in status_repairs.iterrows():
            category = repair.get('category', 'Other') if pd.notna(repair.get('category')) else 'Other'

            # Repair card
            st.markdown(f"""
                <div class='repair-card'>
                    <div style='display: flex; align-items: center;'>
                        <div style='flex: 1;'>
                            <h4>{REPAIR_CATEGORIES[category]['icon']} {repair['customer_name']}</h4>
                            <div class='category-tag' style='background-color: {REPAIR_CATEGORIES[category]["color"]}20; color: {REPAIR_CATEGORIES[category]["color"]};'>
                                {category}
                            </div>
                        </div>
                    </div>
                    <p><strong>📱 Device:</strong> {repair['device']}</p>
                    <p><strong>📞 Phone:</strong> {repair['phone']}</p>
                    <p><strong>💬 Issue:</strong> {repair['issue']}</p>
                    <p><strong>💰 Cost:</strong> ${float(repair['estimated_cost']):.2f}</p>
                """, unsafe_allow_html=True)

            # Display photo if available
            if 'photo_path' in repair and pd.notna(repair['photo_path']):
                photo_data = st.session_state.data_manager.get_photo_as_base64(repair['photo_path'])
                if photo_data:
                    st.markdown(f"""
                        <div class='photo-container'>
                            <img src="data:image/jpeg;base64,{photo_data}" alt="Customer Photo"/>
                        </div>
                    """, unsafe_allow_html=True)

            # Add edit button
            if st.button("✏️ Edit", key=f"edit_{repair.name}"):
                st.session_state.editing_repair = repair.name

            st.markdown("</div>", unsafe_allow_html=True)

        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)

    # Edit modal (show when editing_repair is set)
    if hasattr(st.session_state, 'editing_repair'):
        idx = st.session_state.editing_repair
        repair = repairs_df.loc[idx]

        with st.form(key=f"edit_form_{idx}"):
            st.subheader(f"Edit Repair - {repair['customer_name']}")

            col1, col2 = st.columns(2)
            with col1:
                updated_name = st.text_input("Customer Name", repair['customer_name'])
                updated_phone = st.text_input("Phone", repair['phone'])
                updated_device = st.text_input("Device", repair['device'])
            with col2:
                updated_category = st.selectbox(
                    "Category",
                    options=list(REPAIR_CATEGORIES.keys()),
                    index=list(REPAIR_CATEGORIES.keys()).index(repair.get('category', 'Other')),
                )
                updated_status = st.selectbox(
                    "Status",
                    ["Pending", "In Progress", "Waiting for Parts", "Ready for Pickup", "Completed"],
                    index=["Pending", "In Progress", "Waiting for Parts", "Ready for Pickup", "Completed"].index(repair['status'])
                )

            updated_issue = st.text_area("Issue Description", repair['issue'])
            updated_cost = st.number_input("Cost", min_value=0.0, value=float(repair['estimated_cost']), format="%.2f")
            new_photo = st.camera_input("Update Photo")

            col1, col2 = st.columns(2)
            with col1:
                if st.form_submit_button("💾 Save Changes"):
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

                    # Save changes
                    repairs_df.to_csv(f"{st.session_state.data_manager.data_dir}/repairs.csv", index=False)
                    del st.session_state.editing_repair
                    st.success("✅ Changes saved successfully!")
                    st.rerun()

            with col2:
                if st.form_submit_button("❌ Cancel"):
                    del st.session_state.editing_repair
                    st.rerun()