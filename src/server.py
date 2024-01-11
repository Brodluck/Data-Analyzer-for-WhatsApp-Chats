"""
    To run this, you gotta have installed streamlit:
        pip3 install streamlit 
        
    then:
        streamlit run server.py
"""
import streamlit as st
import os, hashlib, json
import pandas as pd
import matplotlib.pyplot as plt
from dotenv import load_dotenv
from PIL import Image
from benchpress_parser import *
from io import StringIO
import replicate

def load_hash_dictionary(file_path):
    if os.path.exists(file_path):
        try:
            with open(file_path, "r") as f:
                return json.load(f)
        except json.JSONDecodeError:
            return {}
    else:
        return {}

def save_hash_dictionary(file_path, hash_dict):
    with open(file_path, "w") as f:
        json.dump(hash_dict, f)

def save_uploaded_file(uploaded_file, hash_dict_file='hash_dict.json'):
    file_hash = hashlib.md5(uploaded_file.getvalue()).hexdigest()
    hash_dict_path = os.path.join(os.path.dirname(__file__), '..', 'resources/dicts', hash_dict_file)
    hash_dict = load_hash_dictionary(hash_dict_path)
    
    if file_hash in hash_dict:
        st.error('This file has already been uploaded.')
        return None
    
    file_name = f"{uploaded_file.name}"
    file_path = os.path.join(os.path.dirname(__file__), '..', 'resources/uploaded_chats', file_name)
    
    with open(file_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    
    hash_dict[file_hash] = uploaded_file.name
    save_hash_dictionary(hash_dict_path, hash_dict)
    return file_path

def list_uploaded_files():
    files_path = os.path.join(os.path.dirname(__file__), '..', 'resources/uploaded_chats')
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

def get_unique_dates_from_chat(file_path):
    with open(file_path, "r") as file:
        stringio = StringIO(file.read())
        messages = parser(stringio)

    unique_dates = sorted({message['date'].strftime("%Y-%m-%d") for message in messages})
    return unique_dates

def filter_messages_by_date(messages, selected_date):
    return [msg for msg in messages if msg['date'].strftime("%Y-%m-%d") == selected_date]

def main():
    st.set_page_config(page_title="BenchPress Labs", layout="wide")
    css_path = os.path.join(os.path.dirname(__file__), "style.css")
    st.markdown(f'<style>{load_css(css_path)}</style>', unsafe_allow_html=True)
    st.title("WhatsApp Analyzer by Benchpress Labs")
    
    #AI LLM stuff
    # load_dotenv()
    # api_token = os.getenv('REPLICATE_API_TOKEN')
    # client = replicate.Client(api_token=api_token)

    with st.sidebar:
        uploaded_files = list_uploaded_files()
        selected_file = st.selectbox("Uploaded Chats", uploaded_files)

        if selected_file:
            file_path = os.path.join(os.path.dirname(__file__), '..', 'resources/uploaded_chats', selected_file)
            st.session_state['file_path'] = file_path
            unique_dates = get_unique_dates_from_chat(file_path)
            selected_date = st.selectbox("Select Date for ChatBot", unique_dates)

        st.sidebar.write("ChatBot")
        if 'chat_history' not in st.session_state:
            st.session_state['chat_history'] = []

        user_input = st.sidebar.text_input("Type your message here:", key="chat_input")
        if st.sidebar.button("Send"):
            if 'file_path' in st.session_state and os.path.exists(st.session_state['file_path']):
                with open(st.session_state['file_path'], "r") as file:
                    stringio = StringIO(file.read())
                    messages = parser(stringio)
                    filtered_messages = filter_messages_by_date(messages, selected_date)

                # Prepare chat data for LLM
                chat_text = " ".join([f"{msg['sender']}: {msg['message']};" for msg in filtered_messages])
                combined_input = f"\"{chat_text}\"\nWith this messages data, answer this question: {user_input}"
                # print(combined_input)
                # Query the LLM model
                # Adjust the following as per your LLM configuration
                client = replicate.Client(api_token="")
                # bot_response = client.predictions.create(
                for event in replicate.stream(
                  "meta/llama-2-70b-chat",
                    input={
                        "debug": False,
                        "top_p": 1,
                        "prompt": combined_input,
                        "temperature": 0.5,
                        "system_prompt": "You are a helpful, respectful and honest assistant. You will help to analyze WhatApp's chats conversations. You will get the conversations already parsed, each message have the name or their number if the contact is not added, and then after a colon (:) will be the message. They will be separated for the next message by a semicolon (;) even when the sender were the same",
                        "max_new_tokens": 500,
                        "min_new_tokens": -1
                    },
                ):
                    print(str(event), end="")
                st.session_state['chat_history'].append(("Bot", str(event)))

                # Clear the user input field
                st.session_state.chat_input = ""

            else:
                st.sidebar.error("Please select an uploaded chat file first.")

        # Display chat history
        for author, message in st.session_state['chat_history']:
            st.sidebar.write(f"{author}: {message}")

    with st.container():
        uploaded_file = st.file_uploader("Upload your WhatsApp chat file here (Drag and drop or click to browse)", 
                                        type=["txt"], 
                                        help="Drag and drop your WhatsApp chat file here",
                                        label_visibility="collapsed")
        
        if uploaded_file is not None:
            # file_path = save_uploaded_file(uploaded_file)
            st.session_state['file_path'] = save_uploaded_file(uploaded_file)
            # st.sidebar.markdown(f"You are viewing: **{uploaded_file.name}**")


        text_search = st.text_input("Search messages by keywords", value="")
        if text_search:
            with open(os.path.join(os.path.dirname(__file__), '..', 'resources/uploaded_chats', selected_file), "r") as file:
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
            with open(os.path.join(os.path.dirname(__file__), '..', 'resources/uploaded_chats', selected_file), "r") as file:
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
                user_most_used_word = calculate_most_used_word_per_user(messages)
                most_used_word_df = pd.DataFrame([
                    {"Sender": sender, "Word": word, "Count": count}
                    for sender, (word, count) in user_most_used_word.items()
                ])
                st.subheader("Top Used Words per User")
                st.table(most_used_word_df)

                with st.expander("View Analysis"):
                    cols = st.columns(3)
                    files = ["sender_count_plot.png", "sender_percentage_plot.png", "time_ranges_plot.png"]
                    for i, file in enumerate(files):
                        image = Image.open(file)
                        cols[i].image(image, use_column_width=True)

if __name__ == "__main__":
    main()