import benchpress_parser as bp
import os
import pandas as pd

if __name__ == "__main__":
    file_path = os.path.join(os.path.dirname(__file__), '..', 'resources', 'sample.txt')

    with open(file_path, 'r', encoding='utf-8') as file:
        messages = bp.parser(file)
    
    df = pd.DataFrame(messages, columns=['date', 'time', 'sender', 'message'])
    print(df)

    sender_count, sender_percentage, time_ranges, total_messages, num_senders, first_message_date = bp.analyze_chat_data(messages)
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

    print(f'\nTotal messages: {total_messages}')
    print(f'Total senders: {num_senders}')
    print(f'First message was sent on {first_message_date}')