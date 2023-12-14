"""
    To run this, you gotta have installed streamlit:
        pip3 install streamlit 
        
    then:
        streamlit run server.py
    
    To check the website: http://localhost:8501/ the port is automatically assigned 

"""
import streamlit as st
import os
import matplotlib.pyplot as plt
from benchpress_parser import *
from io import StringIO

def save_uploaded_file(uploaded_file):
    with open(os.path.join(os.path.dirname(__file__), '..', 'resources', 'uploaded.txt'), "wb") as f:
        f.write(uploaded_file.getbuffer())
    return st.success(f"Saved file: {uploaded_file.name} in uploaded_files directory")

def plot_sender_count(sender_count):
    plt.bar(sender_count.keys(), sender_count.values())
    plt.xlabel('Sender')
    plt.ylabel('Number of Messages')
    plt.title('Message Count per Sender')
    plt.xticks(rotation=45)
    plt.tight_layout()
    st.pyplot(plt)

def plot_time_ranges(time_ranges):
    plt.plot(range(len(time_ranges)), time_ranges)
    plt.xlabel('Time Range')
    plt.ylabel('Number of Messages')
    plt.title('Message Density Over Time')
    st.pyplot(plt)

import matplotlib.pyplot as plt
import streamlit as st

def plot_sender_percentage(sender_percentage, filename="sender_percentage_plot.png"):
    labels = sender_percentage.keys()
    sizes = sender_percentage.values()
    plt.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=140)
    plt.axis('equal')
    plt.title('Percentage of Messages Sent by Each Sender')
    plt.savefig(filename)
    plt.clf()

def main():
    st.set_page_config(page_title="BenchPress Labs", layout="wide")
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
    st.title("WhatsApp Analyzer by Benchpress Labs")
    uploaded_file = st.file_uploader("Upload your WhatsApp chat file here (Drag and drop or click to browse)", 
                                 type=["txt"], 
                                 help="Drag and drop your WhatsApp chat file here",
                                 label_visibility="collapsed")
    analysis_done = False
    if uploaded_file is not None:
        save_uploaded_file(uploaded_file)
        with open(file_path, 'r', encoding='utf-8') as file:
            messages = parser(file)
        sender_count, sender_percentage, time_ranges = analyze_chat_data(messages)

        with st.expander("View Analysis"):
            if sender_count:
                plot_sender_count(sender_count)
            if sender_percentage:
                plot_sender_percentage(sender_percentage)
            if time_ranges:
                plot_time_ranges(time_ranges)
            
            analysis_done = True

    if analysis_done:        
        if st.button('Clear Analysis'):
            st.rerun()


            
if __name__ == "__main__":
    main()

