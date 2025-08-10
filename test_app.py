"""
Minimal test app to debug loading issues
"""
import streamlit as st

st.set_page_config(
    page_title="Test ETL Tool",
    page_icon="🔧",
    layout="wide"
)

st.title("🔧 ETL Automation Tool v2.0 - Test Version")

st.write("If you can see this, the basic Streamlit app is working!")

# Test session state
if 'test_counter' not in st.session_state:
    st.session_state.test_counter = 0

if st.button("Test Button"):
    st.session_state.test_counter += 1
    st.write(f"Button clicked {st.session_state.test_counter} times")

st.write("✅ Basic functionality is working!")

# Test API connection
try:
    import requests
    response = requests.get("http://localhost:8000/")
    if response.status_code == 200:
        st.success("✅ Backend API is reachable!")
        st.json(response.json())
    else:
        st.error(f"❌ Backend API returned status {response.status_code}")
except Exception as e:
    st.error(f"❌ Cannot connect to backend API: {e}")

st.write("🔧 Debug complete!")
