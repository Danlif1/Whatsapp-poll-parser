from datetime import datetime
import blackboxprotobuf
from main import path_to_db, people_map
from session_file import Session


# Translating poll data into a map.
def translate_data(byte_data):
    # Decoding the data.
    message, typedef = blackboxprotobuf.decode_message(byte_data)
    # message['8'] is the actual poll.
    # message['8']['2'] is the header/question of the poll.
    header = message['8']['2'].decode('utf8')
    options = []
    # message['8']['3'] is the options of the poll, it's in a list format.
    for _message in message['8']['3']:
        # for each _message in message, _message['1'] is the option.
        options.append(_message['1'].decode('utf8'))
    votes_for = [0] * len(options)
    # message['8']['5'] is the votes per person, it's in a list format.
    for _message in message['8']['5']:
        try:
            # The actual votes can be either in a list (multiple votes) or in an int format (single vote).
            if isinstance(_message['1'], list):
                # _message['1'] is the votes.
                for _vote in _message['1']:
                    votes_for[_vote] += 1
            else:
                # _message['1'] is the vote.
                votes_for[_message['1']] += 1
        except:
            # If a person removed all his votes from the poll he will still appear but will have no votes.
            pass
    try:
        # message['8']['6'] is my vote, it is always in a map format (there is only one me).
        if isinstance(message['8']['6']['1'], list):
            for _vote in message['8']['6']['1']:
                votes_for[_vote] += 1
        else:
            votes_for[message['8']['6']['1']] += 1
    except:
        pass
    # Creating the result.
    result = {"header": header, "options": options, "votes": votes_for}
    return result


# Extracting the polls from the database.
def extract_polls(chat_name):
    polls = []
    # Starting a session with the database.
    session = Session(path_to_db)
    # Getting the chat id.
    my_chat = session.get_chat_id(chat_name)
    # Getting the polls from the chat.
    my_messages = session.get_messages_by_chat_id_and_type(my_chat, 46)
    for message in my_messages:
        # Getting the poll header/question, options and votes.
        poll = message.get_info(raw=False)
        # Adding the creator.
        poll['creator'] = message.get_sender()
        if poll['creator'] is None:
            # If there is no creator it is me.
            poll['creator'] = 'דניאל'
        # Adding the time of the poll.
        poll['time'] = message.get_time()
        # Adding the poll to the polls list.
        polls.append(poll)
    return polls


def extract_poll_data(chat_name):
    # Every line in the polls excel,
    # first line isn't from whatsapp and is the title of each column,
    # see commented code to see how to generate (bottom of the page in main).
    all_polls = [
        ['', 'יוצר הסקר', 'תאריך הסקר', 'כותרת הסקר', 'אופציה 1', 'מספר עונים על 1', 'אופציה 2', 'מספר עונים על 2',
         'אופציה 3', 'מספר עונים על 3', 'אופציה 4', 'מספר עונים על 4', 'אופציה 5', 'מספר עונים על 5', 'אופציה 6',
         'מספר עונים על 6', 'אופציה 7', 'מספר עונים על 7', 'אופציה 8', 'מספר עונים על 8', 'אופציה 9', 'מספר עונים על 9',
         'אופציה 10', 'מספר עונים על 10', 'אופציה 11', 'מספר עונים על 11', 'אופציה 12', 'מספר עונים על 12',
         'תאריך בדיקה אחרון', 'בודק אחרון']]
    # Extracting the polls using the chats name.
    polls = extract_polls(chat_name)
    poll_number = 1
    for poll in polls:
        # Every parsed poll starts with the poll number.
        single_poll = [poll_number]
        poll_number += 1
        try:
            # Trying to add the creators name in the map.
            single_poll.append(people_map[poll['creator']])
        except:
            # Failed to add the creators name in the map, using the default name.
            print("error", people_map)
            single_poll.append(poll['creator'])
        # Adding the time the poll was created.
        single_poll.append(poll['time'])
        # Adding the header/question of the poll.
        single_poll.append(poll['header'])
        for actual_index, option in enumerate(poll['options']):
            # Adding the option and next to it its vote.
            single_poll.append(option)
            single_poll.append(poll['votes'][actual_index])
        # Adding the time of the update.
        today = datetime.now()
        today = today.strftime("%d.%m.%y %H:%M")
        single_poll.append(today)
        # Adding the updater. (Me)
        single_poll.append("דניאל")
        # Adding the poll to the poll list.
        all_polls.append(single_poll)
    return all_polls
