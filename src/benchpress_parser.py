import re, os
from datetime import datetime
from pprint import pprint

# the return value of the parser function looks like this:
# [message1 : dict, message2 : dict, message3 : dict, ...]

# each message is a dictionary with the following keys:
# date: datetime.date
# time: datetime.time
# sender: string
# message: string

def parser(file):
    chat_data = [] # list of dictionaries, each dictionary representing a message
    
    for line in file:
        if 'end-to-end encrypted' in line or 'created group' in line or 'added you' in line or '<Media omitted>' in line or 'This message was deleted' in line:
            continue
        line = line.replace('\u202f', ' ') # remove non-breaking spaces
        pattern = r"(\d{1,2}/\d{1,2}/\d{2}), (\d{1,2}:\d{2}\s[APM]{2}) - (.*?): (.*)"
        match = re.match(pattern, line)
        if match:
            date_str, time_str, sender, message = match.groups()
            date, time = datetime.strptime(date_str, '%d/%m/%y'), datetime.strptime(time_str, '%I:%M %p').time()
            chat_data.append({'date': date, 'time': time, 
                              'sender': sender, 'message': message})
        else:
            pattern = r"(\d{1,2}/\d{1,2}/\d{2}), (\d{1,2}:\d{2}\s[APM]{2}) - (.*)"
            match = re.match(pattern, line)
            if match:
                date_str, time_str, message = match.groups()
                sender, date, time = 'Chat Information', datetime.strptime(date_str, '%d/%m/%y'), datetime.strptime(time_str, '%I:%M %p').time()
                    
                chat_data.append({'date': date, 'time': time, 'sender': sender, 'message': message})
    return chat_data

if __name__ == "__main__":
    file_path = os.path.join(os.path.dirname(__file__), '..', 'resources', 'sample.txt')

    with open(file_path, 'r', encoding='utf-8') as file:
        messages = parser(file)
    
    for message in messages:
        pprint(message)