"""
    To run this, you gotta have installed streamlit:
        pip3 install streamlit 
        
    then:
        streamlit run server.py
    
"""
import streamlit as st
import os, hashlib
import pandas as pd
from PIL import Image
import matplotlib.pyplot as plt
from benchpress_parser import *
from io import StringIO

def save_uploaded_file(uploaded_file):
    file_hash = hashlib.md5(uploaded_file.getvalue()).hexdigest()
    file_name = f"{file_hash}_{uploaded_file.name}"
    file_path = os.path.join(os.path.dirname(__file__), '..', 'resources', file_name)

    if not os.path.exists(file_path):
        with open(file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        return file_path

    return file_path

def list_uploaded_files():
    files_path = os.path.join(os.path.dirname(__file__), '..', 'resources')
    return [f for f in os.listdir(files_path) if os.path.isfile(os.path.join(files_path, f))]

def process_user_input(user_input):
    return "Echo: " + user_input

def plot_time_ranges(time_ranges, filename="time_ranges_plot.png"):
    fig, ax = plt.subplots()
    ax.plot(range(len(time_ranges)), time_ranges)
    ax.set_xlabel('Time Range')
    ax.set_ylabel('Number of Messages')
    ax.set_title('Message Density Over Time')
    fig.savefig(filename)
    plt.close(fig) 

def plot_sender_count(sender_count, filename="sender_count_plot.png"):
    fig, ax = plt.subplots()
    ax.bar(sender_count.keys(), sender_count.values())
    ax.set_xlabel('Sender')
    ax.set_ylabel('Number of Messages')
    ax.locator_params(axis='y', integer=True)
    ax.set_title('Message Count per Sender')
    ax.tick_params(axis='x', rotation=45)
    fig.tight_layout()
    fig.savefig(filename)
    plt.close(fig)

def plot_sender_percentage(sender_percentage, filename="sender_percentage_plot.png"):
    fig, ax = plt.subplots()
    labels = sender_percentage.keys()
    sizes = sender_percentage.values()
    ax.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=140)
    ax.axis('equal')
    ax.set_title('Percentage of Messages Sent by Each Sender')
    fig.savefig(filename)
    plt.close(fig)

def load_css(file_name):
    with open(file_name, "r") as f:
        return f.read()

def main():
    st.set_page_config(page_title="BenchPress Labs", layout="wide")
    css_path = os.path.join(os.path.dirname(__file__), "style.css")
    st.markdown(f'<style>{load_css(css_path)}</style>', unsafe_allow_html=True)
    st.title("WhatsApp Analyzer by Benchpress Labs")

    with st.sidebar:
        uploaded_files = list_uploaded_files()
        selected_file = st.selectbox("Uploaded Chats", uploaded_files)

    with st.container():
        uploaded_file = st.file_uploader("Upload your WhatsApp chat file here (Drag and drop or click to browse)", 
                                        type=["txt"], 
                                        help="Drag and drop your WhatsApp chat file here",
                                        label_visibility="collapsed")
        
        if uploaded_file is not None:
            file_path = save_uploaded_file(uploaded_file)
            st.sidebar.markdown(f"You are viewing: **{uploaded_file.name}**")


        text_search = st.text_input("Search messages by keywords", value="")
        if text_search:
            with open(os.path.join(os.path.dirname(__file__), '..', 'resources', selected_file), "r") as file:
                stringio = StringIO(file.read())
                messages = parser(stringio)

                results = []
                for message in messages:
                    if text_search.lower() in message['message'].lower():
                        result = {
                            "Date": message['date'].strftime("%Y-%m-%d"),
                            "Time": message['time'].strftime("%H:%M:%S"),
                            "Sender": message['sender'],
                            "Message": message['message']
                        }
                        results.append(result)
                
                if not results:
                    st.warning(f"No messages were found containing '{text_search}'.")
                else:
                    df_results = pd.DataFrame(results)
                    st.dataframe(df_results)

        if selected_file:
            with open(os.path.join(os.path.dirname(__file__), '..', 'resources', selected_file), "r") as file:
                stringio = StringIO(file.read())
                messages = parser(stringio)
                sender_count, sender_percentage, time_ranges, total_messages, num_senders, first_message_date = analyze_chat_data(messages)
            
                plot_sender_count(sender_count)
                plot_sender_percentage(sender_percentage)
                plot_time_ranges(time_ranges)

                st.subheader("Relevant data about your chat")
                st.write("Total number of messages: ", total_messages)
                st.write("Total number of participants: ", num_senders)
                st.write("Date of the first message: ", first_message_date)

                with st.expander("View Analysis"):
                    cols = st.columns(3)
                    files = ["sender_count_plot.png", "sender_percentage_plot.png", "time_ranges_plot.png"]
                    for i, file in enumerate(files):
                        image = Image.open(file)
                        cols[i].image(image, use_column_width=True)

if __name__ == "__main__":
    main()
