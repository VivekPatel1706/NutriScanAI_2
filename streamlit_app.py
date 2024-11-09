import streamlit as st

url = st.secrets["database"]["DB_URL"]
db = st.secrets["database"]["DB_NAME"]
admin_collection = st.secrets["database"]["DB_ADMIN"]
user_collection = st.secrets["database"]["DB_USER"]

st.write("# Welcome to NutriScanAI! ")
st.markdown("NutriScanAI is virtually an AI-Powered Web-Based application that scans a product's ingredient label to identify banned harmful substances in other countries.")
st.markdown("It is AI usage to scan any given ingredients for possible health risks, identify banned substances across different countries.")
st.markdown("NutriScanAI simplifies food safety information in real-time with honest data to help users make healthier choices.")
