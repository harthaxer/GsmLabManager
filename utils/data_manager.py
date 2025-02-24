import pandas as pd
import os
from datetime import datetime
import base64

class DataManager:
    def __init__(self):
        self.data_dir = "data"
        self.photos_dir = os.path.join(self.data_dir, "customer_photos")
        self.ensure_data_files()

    def ensure_data_files(self):
        """Create data files and directories if they don't exist"""
        if not os.path.exists(self.data_dir):
            os.makedirs(self.data_dir)

        if not os.path.exists(self.photos_dir):
            os.makedirs(self.photos_dir)

        # Create sales.csv if it doesn't exist
        if not os.path.exists(f"{self.data_dir}/sales.csv"):
            pd.DataFrame(columns=[
                'date', 'customer_name', 'phone', 'item', 'price', 'payment_method'
            ]).to_csv(f"{self.data_dir}/sales.csv", index=False)

        # Create repairs.csv if it doesn't exist
        if not os.path.exists(f"{self.data_dir}/repairs.csv"):
            pd.DataFrame(columns=[
                'date', 'customer_name', 'phone', 'device', 'category', 'issue', 'status',
                'estimated_cost', 'completion_date', 'photo_path'
            ]).to_csv(f"{self.data_dir}/repairs.csv", index=False)

        # Create inventory.csv if it doesn't exist
        if not os.path.exists(f"{self.data_dir}/inventory.csv"):
            pd.DataFrame(columns=[
                'item_name', 'quantity', 'price', 'threshold'
            ]).to_csv(f"{self.data_dir}/inventory.csv", index=False)

    def save_customer_photo(self, photo_bytes, customer_name):
        """Save customer photo and return the file path"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_name = "".join(x for x in customer_name if x.isalnum())
        filename = f"{safe_name}_{timestamp}.jpg"
        filepath = os.path.join(self.photos_dir, filename)

        with open(filepath, "wb") as f:
            f.write(photo_bytes)

        return filepath

    def get_photo_as_base64(self, photo_path):
        """Convert photo to base64 for display"""
        if photo_path and os.path.exists(photo_path):
            with open(photo_path, "rb") as f:
                return base64.b64encode(f.read()).decode()
        return None

    def get_sales(self):
        return pd.read_csv(f"{self.data_dir}/sales.csv")

    def add_sale(self, sale_data):
        sales_df = self.get_sales()
        sale_data['date'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        # Convert sale_data dict to DataFrame and concatenate
        new_sale_df = pd.DataFrame([sale_data])
        sales_df = pd.concat([sales_df, new_sale_df], ignore_index=True)
        sales_df.to_csv(f"{self.data_dir}/sales.csv", index=False)

    def get_repairs(self):
        return pd.read_csv(f"{self.data_dir}/repairs.csv")

    def add_repair(self, repair_data):
        repairs_df = self.get_repairs()
        repair_data['date'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        # Convert repair_data dict to DataFrame and concatenate
        new_repair_df = pd.DataFrame([repair_data])
        repairs_df = pd.concat([repairs_df, new_repair_df], ignore_index=True)
        repairs_df.to_csv(f"{self.data_dir}/repairs.csv", index=False)

    def update_repair_status(self, index, status):
        repairs_df = self.get_repairs()
        repairs_df.loc[index, 'status'] = status
        if status == "Completed":
            repairs_df.loc[index, 'completion_date'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        repairs_df.to_csv(f"{self.data_dir}/repairs.csv", index=False)

    def get_inventory(self):
        return pd.read_csv(f"{self.data_dir}/inventory.csv")

    def update_inventory(self, inventory_data):
        inventory_data.to_csv(f"{self.data_dir}/inventory.csv", index=False)