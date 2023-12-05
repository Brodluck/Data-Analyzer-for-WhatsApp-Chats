import re # support for regular expressions

def parser(filename):
    chat_data = [] # this'll be a list of dictionaries
    with open(filename, 'r', encoding='utf-8') as file:
        for line in file:
            if 'end-to-end encrypted' in line or 'created group' in line:
                continue

            match = re.match(r'(\d{1,2}/\d{1,2}/\d{2,4}), (\d{1,2}:\d{2}\s[APM]{2}) - (.*?): (.*)', line)
            if match:
                date, time, sender, message = match.groups()

                if "<Media omitted>" in message:
                    continue

                if not sender: # sender is not in contacts, so it's a phone number
                    sender_match = re.search(r'\+\d+', line)
                    if sender_match:
                        sender = sender_match.group()

                chat_data.append({
                    'date': date,
                    'time': time,
                    'sender': sender,
                    'message': message
                })

    return chat_data

# Usage
chat_filename = 'sample.txt'
parsed_chat = parser(chat_filename)
for message in parsed_chat:
    print(message)
