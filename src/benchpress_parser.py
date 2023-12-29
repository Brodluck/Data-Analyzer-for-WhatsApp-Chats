import re, os, string
from datetime import datetime
from collections import Counter

# the return value of the parser function looks like this:
# [message1 : dict, message2 : dict, message3 : dict, ...]

# each message is a dictionary with the following keys:
# date: datetime.date
# time: datetime.time
# sender: string
# message: string

def load_stop_words(filename):
    with open(os.path.join(os.path.dirname(__file__), '..', 'resources', filename), "r") as file:
        return set(file.read().splitlines())

def add_msg_to_chat_data(chat_data, match, is_iphone=False):
    date_str, time_str, sender, message = match.groups()

    if is_iphone:
        time_format = '%H:%M:%S'
    elif 'AM' in time_str or 'PM' in time_str:
        time_format = '%I:%M %p'
    else:
        time_format = '%H:%M'
    
    time = datetime.strptime(time_str, time_format).time()
    
    # Try parsing with four-digit year first, then fall back to two-digit year
    try:
        date = datetime.strptime(date_str, '%d/%m/%Y').date()
    except ValueError:
        date = datetime.strptime(date_str, '%d/%m/%y').date()

    chat_data.append({'date': date, 'time': time, 'sender': sender, 'message': message})


def parser(file) -> list:
    chat_data = []
    android_pattern = r"(\d{1,2}/\d{1,2}/\d{2,4}), (\d{1,2}:\d{1,2}) - (.*?): (.+)"
    iphone_pattern = r"\[(\d{1,2}/\d{1,2}/\d{2,4}), (\d{1,2}:\d{1,2}:\d{1,2})\] (.*?): (.+)"
    multiline_message_buffer = []

    for line in file:
        line = line.strip()

        # Skip lines with system messages
        if any(phrase in line for phrase in ['Messages to this chat and calls are now secured with end-to-end encryption. Tap for more info.', 'Messages and calls are end-to-end encrypted']):
            continue

        # Try matching with Android pattern
        android_match = re.match(android_pattern, line)
        # Try matching with iPhone pattern
        iphone_match = re.match(iphone_pattern, line)

        if android_match:
            # If multiline_message_buffer is not empty, append it to the last chat_data message
            if multiline_message_buffer:
                chat_data[-1]['message'] += ' ' + ' '.join(multiline_message_buffer)
                multiline_message_buffer.clear()
            add_msg_to_chat_data(chat_data, android_match)
        elif iphone_match:
            # If multiline_message_buffer is not empty, append it to the last chat_data message
            if multiline_message_buffer:
                chat_data[-1]['message'] += ' ' + ' '.join(multiline_message_buffer)
                multiline_message_buffer.clear()
            add_msg_to_chat_data(chat_data, iphone_match, is_iphone=True)
        else:
            # If the line doesn't match any pattern, add it to the multiline_message_buffer
            multiline_message_buffer.append(line)

    # If there's anything left in the buffer after processing all lines, append it to the last message
    if multiline_message_buffer and chat_data:
        chat_data[-1]['message'] += ' ' + ' '.join(multiline_message_buffer)

    return chat_data

def analyze_chat_data(messages):
    if not messages:
        return Counter(), {}, [], 0, 0, None

    sender_count = Counter(message['sender'] for message in messages)
    num_senders = len(sender_count)
    
    total_messages = len(messages)
    sender_percentage = {sender: (count / total_messages) * 100 for sender, count in sender_count.items()}
    
    first_message = messages[0]
    first_message_date = datetime.combine(first_message['date'], first_message['time'])

    start_datetime = datetime.combine(messages[0]['date'], messages[0]['time'])
    end_datetime = datetime.combine(messages[-1]['date'], messages[-1]['time'])
    division_span = (end_datetime - start_datetime) / 10

    time_ranges = [0] * 10
    for message in messages:
        message_datetime = datetime.combine(message['date'], message['time'])
        division_index = int((message_datetime - start_datetime) / division_span)
        time_ranges[min(division_index, 9)] += 1

    return sender_count, sender_percentage, time_ranges, total_messages, num_senders, first_message_date

def calculate_most_used_word_per_user(messages):
    stop_words_spanish = load_stop_words('stop_words_spanish.txt')
    user_most_used_words = {}
    
    for message in messages:
        sender = message['sender']
        message_text = message['message']
        
        words = [word.lower() for word in message_text.split() if word.lower() not in stop_words_spanish]
        word_count = Counter(words)
        most_used_word = word_count.most_common(1)
        if sender in user_most_used_words and most_used_word:
            user_most_used_words[sender].append(most_used_word[0][0])
        elif most_used_word:
            user_most_used_words[sender] = [most_used_word[0][0]]
    
    formatted_result = {user: f'"{word}"' for user, words in user_most_used_words.items() for word in words}
    return formatted_result