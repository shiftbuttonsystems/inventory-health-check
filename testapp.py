import streamlit as st
import pandas as pd
import numpy as np

# Set page config
st.set_page_config(
    page_title="Inventory Health Dashboard",
    page_icon="📊",
    layout="wide"
)

# Title
st.title("📊 Inventory Health Analysis")

# Sidebar
with st.sidebar:
    st.header("Settings")
    date_range = st.date_input("Select Date Range")
    category_filter = st.multiselect("Filter Categories", ["Electronics", "Clothing", "Food", "Other"])
    
    # Add a slider
    threshold = st.slider("Low Stock Threshold", 0, 100, 10)

# Main content
col1, col2, col3 = st.columns(3)

with col1:
    st.metric("Total Inventory", "$125,430", "+12%")

with col2:
    st.metric("Low Stock Items", "24", "-8%")

with col3:
    st.metric("Turnover Rate", "3.2", "+0.4")

# Sample data table
st.subheader("Inventory Overview")
data = pd.DataFrame({
    'Product ID': ['P001', 'P002', 'P003', 'P004'],
    'Product Name': ['Laptop', 'Mouse', 'Keyboard', 'Monitor'],
    'Current Stock': [45, 120, 89, 32],
    'Reorder Level': [20, 50, 30, 15],
    'Status': ['OK', 'OK', 'OK', 'Low']
})

st.dataframe(data, use_container_width=True)

# Chart
st.subheader("Stock Level Distribution")
chart_data = pd.DataFrame(np.random.randn(50, 2), columns=['Current Stock', 'Ideal Stock'])
st.line_chart(chart_data)

# Add some text
st.write("""
## Inventory Health Metrics
- **Stockout Risk:** Items below reorder level
- **Excess Inventory:** Items with >90 days supply
- **Optimal Range:** Items within 30-60 days supply
""")