import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta

st.title("Reports and Analytics")

# Get data
sales_df = st.session_state.data_manager.get_sales()
repairs_df = st.session_state.data_manager.get_repairs()

# Date range selector
col1, col2 = st.columns(2)
with col1:
    start_date = st.date_input("Start Date", datetime.now() - timedelta(days=30))
with col2:
    end_date = st.date_input("End Date", datetime.now())

# Convert dates
sales_df['date'] = pd.to_datetime(sales_df['date'])
repairs_df['date'] = pd.to_datetime(repairs_df['date'])

# Filter data by date range
sales_df = sales_df[
    (sales_df['date'].dt.date >= start_date) &
    (sales_df['date'].dt.date <= end_date)
]
repairs_df = repairs_df[
    (repairs_df['date'].dt.date >= start_date) &
    (repairs_df['date'].dt.date <= end_date)
]

# Sales Overview
st.header("Sales Overview")
col1, col2, col3 = st.columns(3)

with col1:
    st.metric("Total Sales", f"${sales_df['price'].sum():.2f}")
with col2:
    st.metric("Average Sale", f"${sales_df['price'].mean():.2f}")
with col3:
    st.metric("Number of Sales", len(sales_df))

# Daily Sales Chart
daily_sales = sales_df.groupby(sales_df['date'].dt.date)['price'].sum().reset_index()
fig_sales = px.line(
    daily_sales,
    x='date',
    y='price',
    title='Daily Sales',
    labels={'price': 'Sales ($)', 'date': 'Date'}
)
st.plotly_chart(fig_sales, use_container_width=True)

# Repair Jobs Overview
st.header("Repair Jobs Overview")
col1, col2 = st.columns(2)

with col1:
    # Repair Status Distribution
    status_counts = repairs_df['status'].value_counts()
    fig_status = px.pie(
        values=status_counts.values,
        names=status_counts.index,
        title='Repair Status Distribution'
    )
    st.plotly_chart(fig_status, use_container_width=True)

with col2:
    # Daily New Repairs
    daily_repairs = repairs_df.groupby(repairs_df['date'].dt.date).size().reset_index()
    daily_repairs.columns = ['date', 'count']
    fig_repairs = px.bar(
        daily_repairs,
        x='date',
        y='count',
        title='Daily New Repair Jobs',
        labels={'count': 'Number of Repairs', 'date': 'Date'}
    )
    st.plotly_chart(fig_repairs, use_container_width=True)

# Payment Method Analysis
st.header("Payment Method Analysis")
payment_counts = sales_df['payment_method'].value_counts()
fig_payment = px.pie(
    values=payment_counts.values,
    names=payment_counts.index,
    title='Payment Method Distribution'
)
st.plotly_chart(fig_payment, use_container_width=True)

# Export Data
st.header("Export Reports")
col1, col2 = st.columns(2)

with col1:
    if st.button("Export Sales Data"):
        csv = sales_df.to_csv(index=False)
        st.download_button(
            label="Download Sales CSV",
            data=csv,
            file_name=f"sales_report_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv"
        )

with col2:
    if st.button("Export Repair Data"):
        csv = repairs_df.to_csv(index=False)
        st.download_button(
            label="Download Repairs CSV",
            data=csv,
            file_name=f"repairs_report_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv"
        )
