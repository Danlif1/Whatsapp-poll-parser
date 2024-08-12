from datetime import datetime
import blackboxprotobuf
from data_handling import path_to_db, get_people_map, message_types, runner
from session_file import Session


# Extracting the polls from the database.
def extract_polls(chat_name):
    polls = []
    # Starting a session with the database.
    session = Session(path_to_db)
    # Getting the chat id.
    my_chat = session.get_chat_id(chat_name)
    # Getting the polls from the chat.
    my_messages = session.get_messages_by_chat_id_and_type(my_chat, message_types["POLL"])
    for message in my_messages:
        # Getting the poll header/question, options and votes.
        poll = message.get_info(raw=False)
        # Sanitize user input.
        if poll['header'][0] == "=":
            poll['header'] = "'" + poll['header']
        for index, option in enumerate(poll['options']):
            if option[0] == "=":
                poll['options'][index] = "'" + option
        # print(message.get_info(raw=True), poll)
        # Adding the creator.
        poll['creator'] = message.get_sender()
        if poll['creator'] is None:
            # If there is no creator it is me.
            poll['creator'] = runner
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
            single_poll.append(get_people_map()[poll['creator']])
        except:
            # Failed to add the creators name in the map, using the default name.
            # print("error", get_people_map())
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
        single_poll.append(runner)
        # Adding the poll to the poll list.
        all_polls.append(single_poll)
    return all_polls
