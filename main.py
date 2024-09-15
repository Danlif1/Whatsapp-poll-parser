import json
from dotenv import load_dotenv
import os

from data_handling import initialize_people, path_to_db
from extarct_polls import extract_poll_data
from extract_data import extract_messages_count
from session_file import Session
from sheets import create_sheet, transfer_sheet


# Sorting the messages in a chat by date order.
def sort_messages(chat_id=None, chat_name=None):
    session = Session(path_to_db)
    # Getting the chat id.

    if not chat_id:
        chat_id = session.get_chat_id(chat_name)
    session.sort_chat_by_date(chat_id)


def main():
    # loading env.
    load_dotenv()
    chat_name = os.getenv("chat_name")
    sheet_id = os.getenv("sheet_id")
    # Initializing people map.
    # sort_messages(chat_name)
    initialize_people()
    # sort_messages(chat_name=chat_name)
    # for i in range(0,1000):
    #     sort_messages(chat_id=i)
    # Extracting the polls from whatsapp database into list of lists.
    poll_data = extract_poll_data(chat_name)
    message_data = extract_messages_count(chat_name)

    # Creating Excel sheet.
    create_sheet(poll_data)
    # Transferring from Excel to Google.
    transfer_sheet("poll_data.xlsx", sheet_id)


if __name__ == "__main__":
    main()


# For the title
def split_custom_pattern(s):
    words = s.split()
    result = []
    pattern = [2, 2, 2, 2, 4, 2, 4, 2, 4, 2, 4, 2, 4, 2, 4, 2, 4, 2, 4, 2, 4, 2, 4, 2, 4, 2, 4, 3, 2]
    index = 0
    pattern_index = 0

    while index < len(words):
        # Determine the current group size based on the pattern
        group_size = pattern[pattern_index % len(pattern)]
        # Create a group of words based on the current group size
        group = words[index:index + group_size]
        # Join the group into a single string and add to the result list
        result.append(' '.join(group))
        # Move the index forward by the size of the current group
        index += group_size
        # Move to the next pattern
        pattern_index += 1

    return result

# # Example usage
# variable = "יוצר הסקר תאריך הסקר כותרת הסקר אופציה 1   מספר עונים על 1    אופציה 2   מספר עונים על 2    אופציה 3   מספר עונים על 3    אופציה 4   מספר עונים על 4    אופציה 5   מספר עונים על 5    אופציה 6   מספר עונים על 6    אופציה 7   מספר עונים על 7    אופציה 8   מספר עונים על 8    אופציה 9   מספר עונים על 9    אופציה 10  מספר עונים על 10   אופציה 11  מספר עונים על 11   אופציה 12  מספר עונים על 12   תאריך בדיקה אחרון  בודק אחרון"
# print(split_custom_pattern(variable))
