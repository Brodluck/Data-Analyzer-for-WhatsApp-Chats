"""
    To run this, we gotta have installed streamlit:
        pip3 install streamlit 
        
    then:
        streamlit run server.py
    
    To check the website: http://localhost:8501/ the port is automatically assigned 

"""

import streamlit as st
import os

def save_uploaded_file(uploaded_file):
    with open(os.path.join(os.path.dirname(__file__), '..', 'resources', 'uploaded.txt'), "wb") as f:
        f.write(uploaded_file.getbuffer())
    return st.success(f"Saved file: {uploaded_file.name} in uploaded_files directory")

def main():
    st.set_page_config(page_title="WhatsApp Analyzer", layout="wide")

    st.markdown("""
        <style>
        .main {
            align-items: center;
            justify-content: center;
        }
        .block-container {
            text-align: center;
            padding-top: 5rem;
        }
        </style>
        """, unsafe_allow_html=True)

    st.title("WhatsApp Analyzer by BenchpressLabs")

    if not os.path.exists('uploaded_files'):
        os.makedirs('uploaded_files')

    uploaded_file = st.file_uploader("", type=["txt"], help="Drag and drop your WhatsApp chat file here")
    if uploaded_file is not None:
        save_uploaded_file(uploaded_file)

if __name__ == "__main__":
    main()

