import re, os, string, emoji
import pandas as pd
import numpy as np
from datetime import datetime
#from pprint import pprint
from collections import Counter

# the return value of the parser function looks like this:
# [message1 : dict, message2 : dict, message3 : dict, ...]

# each message is a dictionary with the following keys:
# date: datetime.date
# time: datetime.time
# sender: string
# message: string

# mensajes por persona, porcentaje sobre el total de mensajes en el grupo
# densidad de mensajes por rango de tiempo
# quien suele hacer el carry de la conver
# palabra mas usada

def parser(file) -> list:
    """Parses exported chat and returns a list of dictionaries, each dictionary representing a message"""
    chat_data = [] # list of dictionaries, each dictionary representing a message
    msg_characters = ['/', ' - ', ':']
    for line in file:
        if 'end-to-end encrypted' in line or 'created group' in line or 'added you' in line or '<Media omitted>' in line or 'This message was deleted' in line:
            continue
        line = line.replace('\u202f', ' ') # remove non-breaking spaces
        line = line.replace('\n', '') # remove newlines
        pattern = r"(\d{1,2}/\d{1,2}/\d{2}), (\d{1,2}:\d{2}\s[APM]{2}) - (.*?): (.*)"
        match = re.match(pattern, line)
        if match:
            date_str, time_str, sender, message = match.groups()
            date, time = datetime.strptime(date_str, '%d/%m/%y'), datetime.strptime(time_str, '%I:%M %p').time()
            chat_data.append({'date': date, 'time': time, 
                              'sender': sender, 'message': message})
        else:
            for char in msg_characters:
                if char in line:
                    pattern = r"(\d{1,2}/\d{1,2}/\d{2}), (\d{1,2}:\d{2}\s[APM]{2}) - (.*)"
                    match = re.match(pattern, line)
                    if match:
                        date_str, time_str, message = match.groups()
                        sender, date, time = 'Chat Information', datetime.strptime(date_str, '%d/%m/%y'), datetime.strptime(time_str, '%I:%M %p').time()
                        chat_data.append({'date': date, 'time': time, 'sender': sender, 'message': message})
                    break
                else:
                    if chat_data[chat_data.__len__() - 1]['message'][-1] in string.punctuation:
                        chat_data[chat_data.__len__() - 1]['message'] += ' ' + line
                    else:
                        chat_data[chat_data.__len__() - 1]['message'] += '. ' + line
                    break
    return chat_data

def analyze_chat_data(messages):
    # count messages by each sender
    sender_count = Counter(message['sender'] for message in messages)

    #percentage of messages by each sender
    total_messages = len(messages)
    sender_percentage = {sender: (count / total_messages) * 100
                         for sender, count in sender_count.items()}

    # density of messages over 10 time divisions
    if total_messages == 0:
        return sender_count, sender_percentage, [0]*10

    start_datetime = datetime.combine(messages[0]['date'], messages[0]['time'])
    end_datetime = datetime.combine(messages[-1]['date'], messages[-1]['time'])
    division_span = (end_datetime - start_datetime) / 10

    time_ranges = [0] * 10
    for message in messages:
        message_datetime = datetime.combine(message['date'], message['time'])
        division_index = int((message_datetime - start_datetime) / division_span)
        time_ranges[min(division_index, 9)] += 1

    return sender_count, sender_percentage, time_ranges

if __name__ == "__main__":
    file_path = os.path.join(os.path.dirname(__file__), '..', 'resources', 'sample.txt')

    with open(file_path, 'r', encoding='utf-8') as file:
        messages = parser(file)
    
    df = pd.DataFrame(messages, columns=['date', 'time', 'sender', 'message'])
    print(df)


    sender_count, sender_percentage, time_ranges = analyze_chat_data(messages)
    print('\n')
    for sender, count in sender_count.items():
        if sender == 'Chat Information':
            print(f'{count} messages were chat information (people added or deleted, new admins, etc).')
        else:
            print(f'{sender} sent a total of {count} messages.')
    print('\n')
    for sender, percentage in sender_percentage.items():
        if sender == 'Chat Information':
            continue
        print(f'{sender} sent {percentage:.2f}% of the total messages.')
    print('\n')
    for i, time_range in enumerate(time_ranges):
        print(f'{time_range} messages were sent between {i*10} and {(i+1)*10} minutes into the chat.')