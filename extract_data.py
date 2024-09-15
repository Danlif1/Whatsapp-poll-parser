from datetime import datetime
import blackboxprotobuf
from data_handling import path_to_db, get_people_map, message_types, runner
from session_file import Session

def sort_function(element):
    return element[0]

def extract_messages_count(chat_name):
    members = {}
    # Starting a session with the database.
    session = Session(path_to_db)
    # Getting the chat id.
    my_chat = session.get_chat_id(chat_name)
    # Getting the messages from the chat.
    my_messages = session.get_messages_by_chat_id(my_chat)
    all_messages = len(my_messages)
    for message in my_messages:
        _message = {'content': message.get_content(), 'time': message.get_time(), 'creator': message.get_sender()}
        # Adding the creator.
        if _message['creator'] is None:
            # If there is no creator it is me.
            _message['creator'] = runner

        if str(_message['creator']) not in members:
            members[str(_message['creator'])] = []  # Create a new list for this key if it doesn't exist
        members[str(_message['creator'])].append(_message)

    messages_data = []
    for member in members:
        try:
            messages_data.append([len(members[member]), len(members[member]) / all_messages, get_people_map()[member]])
            print(get_people_map()[member], member)
        except:
            messages_data.append([len(members[member]), len(members[member]) / all_messages, member])
    messages_data = sorted(messages_data, key=sort_function, reverse=True)
    return messages_data
