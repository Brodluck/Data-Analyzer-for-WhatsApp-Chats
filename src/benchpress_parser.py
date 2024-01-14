import re, os, string, unicodedata
from datetime import datetime
from collections import Counter, defaultdict

# the return value of the parser function looks like this:
# [message1 : dict, message2 : dict, message3 : dict, ...]

# each message is a dictionary with the following keys:
# date: datetime.date
# time: datetime.time
# sender: string
# message: string

def load_stop_words(filename):
    filepath = os.path.join(os.path.dirname(__file__), '..', 'resources', filename)
    with open(filepath, "r", encoding='utf-8') as file:
        stop_words = []
        for line in file:
            words_in_line = line.strip().split(',')
            stop_words.extend(words_in_line)
    return stop_words

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

        if any(phrase in line for phrase in ['Messages to this chat and calls are now secured with end-to-end encryption.\
                                            Tap for more info.', 'Messages and calls are end-to-end encrypted', '<Media omitted>']):
            continue

        android_match = re.match(android_pattern, line)
        iphone_match = re.match(iphone_pattern, line)

        if android_match:
            if multiline_message_buffer:
                chat_data[-1]['message'] += ' ' + ' '.join(multiline_message_buffer)
                multiline_message_buffer.clear()
            add_msg_to_chat_data(chat_data, android_match)
        elif iphone_match:
            if multiline_message_buffer:
                chat_data[-1]['message'] += ' ' + ' '.join(multiline_message_buffer)
                multiline_message_buffer.clear()
            add_msg_to_chat_data(chat_data, iphone_match, is_iphone=True)
        else:
            multiline_message_buffer.append(line)

    if multiline_message_buffer and chat_data:
        chat_data[-1]['message'] += ' ' + ' '.join(multiline_message_buffer)

    return chat_data

def analyze_chat_data(messages):
    if not messages:
        return Counter(), {}, [], 0, 0, None

    messages = [msg for msg in messages]
    sender_count = Counter(message['sender'] for message in messages)
    num_senders = len(sender_count)
    total_messages = len(messages)
    sender_percentage = {sender: (count / total_messages) * 100 for sender, count in sender_count.items()}

    if not messages:
        return Counter(), {}, [], 0, 0, None

    first_message_date = datetime.combine(messages[0]['date'], messages[0]['time'])
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
    user_word_counts = {}
    stop_words_spanish = load_stop_words('stop_words_spanish.txt')
    unwanted_patterns = ["<Multimedia omitido>", "<adjunto:", "omitido>", "<Media omitted>", "Llamada.","q", "Q","null"]

    for message in messages:
        sender = message['sender']
        message_text = message['message']

        if any(unwanted in message_text for unwanted in unwanted_patterns):
            continue

        words = message_text.split()
        filtered_words = [word for word in words if word.lower() not in stop_words_spanish]

        if sender not in user_word_counts:
            user_word_counts[sender] = Counter()
        user_word_counts[sender].update(filtered_words)

    user_most_used_word = {
        user: word_counts.most_common(1)[0] if word_counts else ('None', 0)
        for user, word_counts in user_word_counts.items()
    }

    return user_most_used_word

def get_daily_chats(chat_data):
    daily_chats = defaultdict(list)
    for message in chat_data:
        daily_chats[message['date']].append(message['message'])
    return daily_chats