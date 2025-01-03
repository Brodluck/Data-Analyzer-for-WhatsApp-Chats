import streamlit as st
import os, hashlib, json
import pandas as pd
from groq import Groq
from PIL import Image
from io import StringIO
from plotting import plot_sender_count, plot_sender_percentage, plot_time_ranges
from benchpress_parser import parser, analyze_chat_data, calculate_most_used_word_per_user

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

def load_css(file_name = os.path.join(os.path.dirname(__file__), "style.css")):
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
    
    st.markdown(f'<style>{load_css()}</style>', unsafe_allow_html=True)
    st.title("WhatsApp Analyzer by Benchpress Labs")
    
    #Token for Groq API
    api_key = os.getenv('GROQ_API_KEY')
    groq_client = Groq(api_key=api_key)
    
    with st.sidebar:
        uploaded_files = list_uploaded_files()
        selected_file = st.selectbox("Uploaded Chats", uploaded_files)

        if selected_file:
            file_path = os.path.join(os.path.dirname(__file__), '..', 'resources/uploaded_chats', selected_file)
            st.session_state['file_path'] = file_path
            unique_dates = get_unique_dates_from_chat(file_path)
            selected_date = st.selectbox("Select Date for ChatBot", unique_dates)
            if selected_date:
                with open(file_path, "r") as file:
                    stringio = StringIO(file.read())
                    messages = parser(stringio)
                    filtered_messages = filter_messages_by_date(messages, selected_date)

                    if 'show_full_message' not in st.session_state:
                        st.session_state.show_full_message = False

                    limited_sneak_peek = "\n".join([f"{msg['sender']}: {msg['message']}" for msg in filtered_messages[:5]])
                    full_sneak_peek = "\n".join([f"{msg['sender']}: {msg['message']}" for msg in filtered_messages])

                    with st.expander("Sneak Peek of the Chat"):
                        if not st.session_state.show_full_message:
                            st.write(limited_sneak_peek)
                            if st.button("Show More", key="show_more"):
                                st.session_state.show_full_message = True
                        else:
                            st.write(full_sneak_peek)
                            if st.button("Show Less", key="show_less"):
                                st.session_state.show_full_message = False

                if "messages" not in st.session_state:
                    st.session_state.messages = []

                for message in st.session_state.messages:
                    with st.chat_message(message["role"]):
                        st.markdown(message["content"])

                if prompt := st.chat_input("What would you like to know about the chat?"):
                    st.session_state.messages.append({"role": "user", "content": prompt})
                    with st.chat_message("user"):
                        st.markdown(prompt)

                    chat_text = " ".join([f"{msg['sender']}: {msg['message']};" for msg in filtered_messages])
                    combined_input = f"\"{chat_text}\"\nWith this data, answer this question: {prompt}"

                    with st.chat_message("assistant"):
                        response = groq_client.chat.completions.create(
                            messages=[
                                {
                                    "role": "system",
                                    "content": "You are a helpful, respectful and honest assistant. Always answer as helpfully as possible, while being safe. Your answers should not include any harmful, unethical, racist, sexist, toxic, dangerous, or illegal content. Please ensure that your responses are socially unbiased and positive in nature.\n\nIf a question does not make any sense, or is not factually coherent, explain why instead of answering something not correct. If you don't know the answer to a question, please don't share false information."
                                },
                                {
                                    "role": "user",
                                    "content": combined_input
                                }
                            ],
                            model="mixtral-8x7b-32768",
                            temperature=0.5,
                            max_tokens=500,
                        )
                        full_response = response.choices[0].message.content
                        st.markdown(full_response)
                        
                    st.session_state.messages.append({"role": "assistant", "content": full_response})

    with st.container():
        uploaded_file = st.file_uploader("Upload your WhatsApp chat file here (Drag and drop or click to browse)", 
                                        type=["txt"], 
                                        help="Drag and drop your WhatsApp chat file here",
                                        label_visibility="collapsed")
        
        if uploaded_file is not None:
            st.session_state['file_path'] = save_uploaded_file(uploaded_file)

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
                        cols[i].image(image)

if __name__ == "__main__":
    main()