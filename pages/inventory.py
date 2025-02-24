import streamlit as st
import pandas as pd

st.title("Inventory Management")

# Get current inventory
inventory_df = st.session_state.data_manager.get_inventory()

# Add new item form
with st.expander("Add New Item"):
    with st.form("inventory_form"):
        item_name = st.text_input("Item Name")
        quantity = st.number_input("Quantity", min_value=0)
        price = st.number_input("Price", min_value=0.0, format="%.2f")
        threshold = st.number_input("Low Stock Threshold", min_value=0)
        
        submit_button = st.form_submit_button("Add Item")
        
        if submit_button:
            if item_name and quantity >= 0 and price >= 0:
                new_item = pd.DataFrame({
                    'item_name': [item_name],
                    'quantity': [quantity],
                    'price': [price],
                    'threshold': [threshold]
                })
                inventory_df = pd.concat([inventory_df, new_item], ignore_index=True)
                st.session_state.data_manager.update_inventory(inventory_df)
                st.success("Item added successfully!")
            else:
                st.error("Please fill all required fields!")

# Display current inventory
st.header("Current Inventory")

# Filter for low stock items
show_low_stock = st.checkbox("Show Low Stock Items Only")
if show_low_stock:
    inventory_df = inventory_df[inventory_df['quantity'] <= inventory_df['threshold']]

# Display inventory table with edit capabilities
edited_df = st.data_editor(
    inventory_df,
    num_rows="dynamic",
    use_container_width=True,
    column_config={
        "quantity": st.column_config.NumberColumn(
            "Quantity",
            min_value=0,
            format="%d"
        ),
        "price": st.column_config.NumberColumn(
            "Price",
            min_value=0.0,
            format="$%.2f"
        ),
        "threshold": st.column_config.NumberColumn(
            "Low Stock Threshold",
            min_value=0,
            format="%d"
        )
    }
)

# Save changes button
if st.button("Save Changes"):
    st.session_state.data_manager.update_inventory(edited_df)
    st.success("Inventory updated successfully!")

# Low stock alerts
low_stock_items = inventory_df[inventory_df['quantity'] <= inventory_df['threshold']]
if not low_stock_items.empty:
    st.warning("### Low Stock Alerts")
    for _, item in low_stock_items.iterrows():
        st.write(f"⚠️ **{item['item_name']}** is running low! ({item['quantity']} remaining)")
