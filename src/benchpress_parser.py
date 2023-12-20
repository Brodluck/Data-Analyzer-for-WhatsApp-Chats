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

def add_msg_to_chat_data(chat_data, match):
    date_str, time_str, sender, message = match.groups()
    if 'AM' in time_str or 'PM' in time_str:
        time = datetime.strptime(time_str, '%I:%M %p').time()
    else:
        time = datetime.strptime(time_str, '%H:%M').time()
    date = datetime.strptime(date_str, '%d/%m/%y')
    chat_data.append({'date': date, 'time': time, 
                      'sender': sender, 'message': message})


def parser(file) -> list:
    """Parses exported chat and returns a list of dictionaries, each dictionary representing a message"""
    chat_data = [] # list of dictionaries, each dictionary representing a message
    msg_characters = ['/', ' - ', ':']
    for line in file:
        if 'end-to-end encrypted' in line or 'created group' in line or 'added you' in line or '<Media omitted>' in line or 'This message was deleted' in line:
            continue
        line = line.replace('\u202f', ' ') # remove non-breaking spaces
        line = line.replace('\n', '') # remove newlines
        # pattern = r"(\d{1,2}/\d{1,2}/\d{2}), (\d{1,2}:\d{2}\s[APM]{2}) - (.*?): (.*)"
        # match = re.match(pattern, line)
        # if match:
        #     add_msg_to_chat_data(chat_data, match)
        # if 'AM - ' in line or 'PM - ' not in line:
        pattern = r"(\d{1,2}/\d{1,2}/\d{2}), (\d{1,2}:\d{2}) - (.*?): (.*)" # 24 hour format
        match = re.match(pattern, line)
        if match:
            add_msg_to_chat_data(chat_data, match)
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
                    while line == '':
                        line = next(file)
                    if chat_data[chat_data.__len__() - 1]['message'][-1] in string.punctuation:
                        chat_data[chat_data.__len__() - 1]['message'] += ' ' + line
                    else:
                        chat_data[chat_data.__len__() - 1]['message'] += '. ' + line
                    break
    return chat_data

def analyze_chat_data(messages):
    # count messages by each sender
    sender_count = Counter(message['sender'] for message in messages)
    num_senders = len(sender_count)
    
    
    #percentage of messages by each sender
    total_messages = len(messages)
    sender_percentage = {sender: (count / total_messages) * 100
                         for sender, count in sender_count.items()}
    
    #date time of the first message sended
    first_message = messages[0]
    first_message_date = datetime.combine(first_message['date'], first_message['time'])


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

    return sender_count, sender_percentage, time_ranges, total_messages, num_senders, first_message_date

def calculate_most_used_word_per_user(messages):
    stop_words_spanish = {
        'de', 'la', 'el', 'en', 'y', 'a', 'que', 'se', 'del', 'las', 'los', 'por', 'un', 'con', 'no', 'una', 'su',
        'para', 'es', 'al', 'lo', 'como', 'más', 'pero', 'sus', 'le', 'ya', 'o', 'este', 'sí', 'porque', 'esta', 'entre',
        'cuando', 'muy', 'sin', 'sobre', 'también', 'me', 'hasta', 'hay', 'donde', 'quien', 'desde', 'todo', 'nos', 'durante',
        'todos', 'uno', 'les', 'ni', 'contra', 'otros', 'ese', 'eso', 'ante', 'ellos', 'e', 'esto', 'mí', 'antes', 'algunos',
        'qué', 'unos', 'yo', 'otro', 'otras', 'otra', 'él', 'tanto', 'esa', 'estos', 'mucho', 'quienes', 'nada', 'muchos',
        'cual', 'poco', 'ella', 'estar', 'estas', 'algunas', 'nosotros', 'otras', 'otra', 'él', 'tanto', 'mía', 'tuyas',
        'otras', 'suyo', 'nuestro', 'vosotros', 'vuestra', 'vuestros', 'vuestras', 'esos', 'esas', 'estoy', 'estás', 'está',
        'estamos', 'estáis', 'están', 'esté', 'estés', 'estemos', 'estéis', 'estén', 'estaré', 'estarás', 'estará', 'estaremos',
        'estaréis', 'estarán', 'estaría', 'estarías', 'estaríamos', 'estaríais', 'estarían', 'estaba', 'estabas', 'estábamos',
        'estabais', 'estaban', 'estuve', 'estuviste', 'estuvo', 'estuvimos', 'estuvisteis', 'estuvieron', 'estuviera', 'estuvieras',
        'estuviéramos', 'estuvierais', 'estuvieran', 'estuviese', 'estuvieses', 'estuviésemos', 'estuvieseis', 'estuviesen', 'estando',
        'estado', 'estada', 'estados', 'estadas', 'estad', 'he', 'has', 'ha', 'hemos', 'habéis', 'han', 'haya', 'hayas', 'haya',
        'hayamos', 'hayáis', 'hayan', 'habré', 'habrás', 'habrá', 'habremos', 'habréis', 'habrán', 'habría', 'habrías', 'habríamos',
        'habríais', 'habrían', 'había', 'habías', 'habíamos', 'habíais', 'habían', 'hube', 'hubiste', 'hubo', 'hubimos', 'hubisteis',
        'hubieron', 'hubiera', 'hubieras', 'hubiéramos', 'hubierais', 'hubieran', 'hubiese', 'hubieses', 'hubiésemos', 'hubieseis',
        'hubiesen', 'habiendo', 'habido', 'habida', 'habidos', 'habidas', 'soy', 'eres', 'es', 'somos', 'sois', 'son', 'sea', 'seas',
        'seamos', 'seáis', 'sean', 'seré', 'serás', 'será', 'seremos', 'seréis', 'serán', 'sería', 'serías', 'seríamos', 'seríais',
        'serían', 'era', 'eras', 'éramos', 'erais', 'eran', 'fui', 'fuiste', 'fue', 'fuimos', 'fuisteis', 'fueron', 'fuera', 'fueras',
        'fuéramos', 'fuerais', 'fueran', 'fuese', 'fueses', 'fuésemos', 'fueseis', 'fuesen', 'sintiéndome', 'sintiéndote', 'sintiéndose',
        'sintiéndonos', 'sintiéndoos', 'sintiéndose', 'me', 'te', 'se', 'nos', 'os', 'se', 'tengo', 'tienes', 'tiene', 'tenemos',
        'tenéis', 'tienen', 'he', 'has', 'ha', 'hemos', 'habéis', 'han', 'haya', 'hayas', 'haya', 'hayamos', 'hayáis', 'hayan',
        'habré', 'habrás', 'habrá', 'habremos', 'habréis', 'habrán', 'habría', 'habrías', 'habríamos', 'habríais', 'habrían', 'había',
        'habías', 'habíamos', 'habíais', 'habían', 'hube', 'hubiste', 'hubo', 'hubimos', 'hubisteis', 'hubieron', 'hubiera', 'hubieras',
        'hubiéramos', 'hubierais', 'hubieran', 'hubiese', 'hubieses', 'hubiésemos', 'hubieseis', 'hubiesen', 'habiendo', 'habido',
        'habida', 'habidos', 'habidas'
    }
    
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