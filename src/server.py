"""
    To run this, you gotta have installed streamlit:
        pip3 install streamlit 
        
    then:
        streamlit run server.py
    
    To check the website: http://localhost:8501/ the port is automatically assigned 

"""
import streamlit as st
import os, hashlib
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
    plt.locator_params(axis='y', integer=True)
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

    with st.sidebar:
        uploaded_files = list_uploaded_files()
        selected_file = st.selectbox("Uploaded Chats", uploaded_files)
        st.subheader("Chat Bot")
        if 'chat_history' not in st.session_state:
            st.session_state['chat_history'] = []

        user_input = st.text_input("Type your message here:", key="user_input")

        if st.button("Send"):
            user_message = f"You: {user_input}"
            bot_response = f"AI Bot: (response to '{user_input}')"
            st.session_state['chat_history'].extend([user_message, bot_response])
            st.session_state['user_input'] = ''  # Clears input box after sending, but it doesnt work like I expected

        # Display chat history
        for message in st.session_state['chat_history']:
            st.text(message)

    uploaded_file = st.file_uploader("Upload your WhatsApp chat file here (Drag and drop or click to browse)", 
                                     type=["txt"], 
                                     help="Drag and drop your WhatsApp chat file here",
                                     label_visibility="collapsed")

    text_search = st.text_input("Search messages by keywords", value="")


    if text_search:
        with open(os.path.join(os.path.dirname(__file__), '..', 'resources', selected_file), "r") as file:
            stringio = StringIO(file.read())
            messages = parser(stringio)

            results = []
            for message in messages:
                if text_search in message['message']:
                    results.append(message)

            st.write(results)

    if uploaded_file is not None:
        file_path = save_uploaded_file(uploaded_file)
        st.sidebar.markdown(f"You are viewing: **{uploaded_file.name}**")

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
