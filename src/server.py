"""
    To run this, you gotta have installed streamlit:
        pip3 install streamlit 
        
    then:
        streamlit run server.py
    
    To check the website: http://localhost:8501/ the port is automatically assigned 

"""
import streamlit as st
import os
from PIL import Image
import matplotlib.pyplot as plt
from benchpress_parser import *
from io import StringIO

def save_uploaded_file(uploaded_file):
    with open(os.path.join(os.path.dirname(__file__), '..', 'resources', 'uploaded.txt'), "wb") as f:
        f.write(uploaded_file.getbuffer())
    return st.success(f"Saved file: {uploaded_file.name} in uploaded_files directory")

def plot_time_ranges(time_ranges, filename="time_ranges_plot.png"):
    plt.plot(range(len(time_ranges)), time_ranges)
    plt.xlabel('Time Range')
    plt.ylabel('Number of Messages')
    plt.title('Message Density Over Time')
    plt.savefig(filename)
    plt.clf()

def plot_sender_count(sender_count, filename="sender_count_plot.png"):
    plt.bar(sender_count.keys(), sender_count.values())
    plt.xlabel('Sender')
    plt.ylabel('Number of Messages')
    plt.title('Message Count per Sender')
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig(filename)
    plt.clf()

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
    if 'analysis_done' not in st.session_state:
        st.session_state['analysis_done'] = False
    uploaded_file = st.file_uploader("Upload your WhatsApp chat file here (Drag and drop or click to browse)", 
                                 type=["txt"], 
                                 help="Drag and drop your WhatsApp chat file here",
                                 label_visibility="collapsed")
    if uploaded_file is not None:
        save_uploaded_file(uploaded_file)
        stringio = StringIO(uploaded_file.getvalue().decode("utf-8"))
        messages = parser(stringio)
        sender_count, sender_percentage, time_ranges = analyze_chat_data(messages)

        plot_sender_count(sender_count)
        plot_sender_percentage(sender_percentage)
        plot_time_ranges(time_ranges)
        plt_count = Image.open("sender_count_plot.png")
        plt_percentage = Image.open("sender_percentage_plot.png")
        plt_time_ranges = Image.open("time_ranges_plot.png")

        with st.expander("View Analysis"):
            st.image(plt_count, use_column_width=True)
            st.image(plt_percentage, use_column_width=True)
            st.image(plt_time_ranges, use_column_width=True)
            st.session_state['analysis_done'] = True

    if st.session_state['analysis_done']:
        if st.button('Reset and Analyze New File'):
            st.session_state['analysis_done'] = False
            st.rerun()
    
    os.delete("sender_count_plot.png")
    os.delete("sender_percentage_plot.png")
    os.delete("time_ranges_plot.png")

if __name__ == "__main__":
    main()

