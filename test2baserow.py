import streamlit as st
import requests
import json
from datetime import datetime

st.set_page_config(page_title="Baserow Test", layout="centered")
st.title("🔧 Baserow Connection Test")

# Configuration
st.sidebar.header("Configuration")
base_url = st.sidebar.text_input("Baserow URL", "https://baserowapp.goxmit.com")
table_id = st.sidebar.text_input("Table ID", "854")
token = st.secrets['BASEROW_TOKEN']


# Test functions
def test_connection():
    """Test if we can connect to Baserow"""
    url = f"{base_url}/api/database/rows/table/854/?user_field_names=true"
    headers = {"Authorization": f"Token {token}"}
    
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            user_data = response.json()
            st.success(f"✅ Connected as: {user_data.get('username', 'Unknown')}")
            return True
        else:
            st.error(f"❌ Connection failed: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        st.error(f"❌ Error: {e}")
        return False

def create_contact(email):
    """Create a new contact in Baserow"""
    url = f"{base_url}/api/database/rows/table/{table_id}/?user_field_names=true"
    params = {"user_field_names": "true"}
    headers = {
        "Authorization": f"Token {token}",
        "Content-Type": "application/json"
    }
    data = {
        "email": email,
        "first_name": "Test",
        "last_name": "User",
        "company_name": "Test Company",
        #"role": 1  # Using number as in your API docs
        "created_date": datetime.now().strftime("%Y-%m-%d")
    }
    
    try:
        response = requests.post(url, headers=headers, params=params, json=data)
        if response.status_code == 200:
            result = response.json()
            st.success(f"✅ Contact created! ID: {result.get('id')}")
            st.json(result)
            return result
        else:
            st.error(f"❌ Failed to create contact: {response.status_code}")
            st.write("Response:", response.text)
            return None
    except Exception as e:
        st.error(f"❌ Error: {e}")
        return None

def list_contacts():
    """List existing contacts"""
    url = f"{base_url}/api/database/rows/table/{table_id}/"
    params = {
        "user_field_names": "true",
        "size": "10"  # Limit to 10 results
    }
    headers = {"Authorization": f"Token {token}"}
    
    try:
        response = requests.get(url, headers=headers, params=params)
        if response.status_code == 200:
            data = response.json()
            st.write(f"📋 Found {data.get('count', 0)} contacts")
            
            if data.get('results'):
                for contact in data['results']:
                    st.write(f"- ID: {contact.get('id')}, Email: {contact.get('email')}")
            return data
        else:
            st.error(f"❌ Failed to list contacts: {response.status_code}")
            return None
    except Exception as e:
        st.error(f"❌ Error: {e}")
        return None

# Main app
st.header("Connection Test")
if st.button("Test Connection"):
    test_connection()

st.header("List Existing Contacts")
if st.button("List Contacts"):
    list_contacts()

st.header("Create New Contact")
email = st.text_input("Email address", "test@example.com")
first_name = st.text_input("First Name", "Test")
last_name = st.text_input("Last Name", "User")

if st.button("Create Contact"):
    if email and "@" in email:
        create_contact(email)
    else:
        st.warning("Please enter a valid email address")

st.markdown("---")
st.subheader("API Details")
st.code(f"""API Endpoint: {base_url}/api/database/rows/table/{table_id}/
Method: POST
Headers: Authorization: Token YOUR_TOKEN
Params: user_field_names=true
Body: {{"email": "test@example.com", ...}}""")