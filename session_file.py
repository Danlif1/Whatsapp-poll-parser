import sqlite3
import time
from typing import List
from datetime import datetime, timedelta
from hexdump import hexdump
import hexdump

from data_handling import translate_data, message_types


class Session:
    # Names of tables in the whatsapp sqlite database.
    chats_table = "ZWACHATSESSION"
    messages_table = "ZWAMESSAGE"
    messages_info_table = "ZWAMESSAGEINFO"
    messages_media_table = "ZWAMEDIAITEM"
    group_members_id_table = "ZWAGROUPMEMBER"
    group_members_name_table = "ZWAPROFILEPUSHNAME"

    def __init__(self, path_to_db):
        """Connects to the db"""
        self.conn = sqlite3.connect(path_to_db)
        self.cursor = self.conn.cursor()

    class Chat:
        def __init__(self, id):
            self.id = id

    class Message:
        def __init__(self, id, cursor):
            self.id = id
            self.cursor = cursor

        # Getting the time that the message was sent in the correct format.
        def get_time(self):
            """From messages_table take ZMESSAGEDATE (Z_PK = id)"""
            self.cursor.execute(f"SELECT ZMESSAGEDATE FROM {Session.messages_table} WHERE Z_PK = ?", (self.id,))
            timestamp = self.cursor.fetchone()[0]
            if timestamp:
                original_time = datetime.utcfromtimestamp(timestamp)
                modified_time = original_time + timedelta(days=31 * 365 + 31 // 4,
                                                          hours=3)  # Adding 31 years and 3 hours
                return modified_time.strftime("%d.%m.%y %H:%M")
            return None

        # Getting the sender default name on whatsapp.
        def get_sender(self):
            """
           From messages_table take ZGROUPMEMBER (Z_PK = id)
           From group_members_id_table take ZMEMBERJID (Z_PK = sender_id)
           From group_members_name_table take ZPUSHNAME (ZJID = member_id)
           """
            self.cursor.execute(f"SELECT ZGROUPMEMBER FROM {Session.messages_table} WHERE Z_PK = ?", (self.id,))
            sender_id = self.cursor.fetchone()[0]
            if sender_id:
                self.cursor.execute(f"SELECT ZMEMBERJID FROM {Session.group_members_id_table} WHERE Z_PK = ?",
                                    (sender_id,))
                member_id = self.cursor.fetchone()[0]
                return member_id[:member_id.find('@')]
            return None

        # Getting the content of the message. (The text)
        def get_content(self):
            """From messages_table take ZTEXT (Z_PK = id)"""
            self.cursor.execute(f"SELECT ZTEXT FROM {Session.messages_table} WHERE Z_PK = ?", (self.id,))
            result = self.cursor.fetchone()[0]
            return result

    class Poll(Message):
        def __init__(self, id, cursor):
            super().__init__(id, cursor)

        # Getting the data of the message. (Who saw, poll data and so on...)
        def get_info(self, raw=False):
            """From messages_info_table take ZRECIPIENTINFO (ZMESSAGE = id)"""
            self.cursor.execute(f"SELECT ZRECEIPTINFO FROM {Session.messages_info_table} WHERE ZMESSAGE = ?",
                                (self.id,))
            result = self.cursor.fetchone()[0]
            if raw:
                # The hexdump of the data.
                return result
            # The data in a readable format. (A map of the header, options and votes of the poll)
            return translate_data(result) if result else None

    # Getting the chat id from its name.
    def get_chat_id(self, chat_name) -> int:
        """
       From chats_table take Z_PK (ZPARTNERNAME = chat_name)
       Uses SQL query
       """
        self.cursor.execute(f"SELECT Z_PK FROM {Session.chats_table} WHERE ZPARTNERNAME = ?", (chat_name,))
        result = self.cursor.fetchone()
        return result[0] if result else None

    # Getting the messages ids from the chat.
    def get_messages_by_chat_id(self, chat_id) -> List[Message]:
        """
       From messages_table take all Z_PK (ZCHATSESSION = chat_id) sort by ZMESSAGEDATE (low to high)
       Uses SQL query
       """
        self.cursor.execute(
            f"SELECT Z_PK FROM {Session.messages_table} WHERE ZCHATSESSION = ? ORDER BY ZMESSAGEDATE ASC", (chat_id,))
        return [Session.Message(id=row[0], cursor=self.cursor) for row in self.cursor.fetchall()]

    # Getting the members phone number in whatsapp format.
    def get_members_by_chat_id(self, chat_id) -> List[str]:
        """
       From group_members_id_table get all ZMEMBERJID and put into a list (ZCHATSESSION = chat_id)
       return the list
       """
        self.cursor.execute(f"SELECT ZMEMBERJID FROM {Session.group_members_id_table} WHERE ZCHATSESSION = ?",
                            (chat_id,))
        return [row[0] for row in self.cursor.fetchall()]

    def update_chat_session(self, chat_id):
        self.cursor.execute(
            f"SELECT Z_OPT, ZMESSAGECOUNTER, ZLASTMESSAGE FROM {Session.chats_table} WHERE ZCHATSESSION = ?",
            (chat_id,))
        (previous_Z_OPT, previous_ZMESSAGECOUNTER, previous_ZLASTMESSAGE) = self.cursor.fetchall()

        current_unix_time = time.time()
        epoch_start = datetime(2001, 1, 1)
        epoch_start_unix = int((epoch_start - datetime(1970, 1, 1)).total_seconds())
        adjusted_time_unix = current_unix_time - epoch_start_unix
        adjusted_time_unix += 7200
        current_date = datetime(1970, 1, 1) + timedelta(seconds=adjusted_time_unix)

        self.cursor.execute(
            f"UPDATE {Session.chats_table} PUT Z_OPT = ?, ZMESSAGECOUNTER = ?, ZLASTMESSAGE = ?, ZLASTMESSAGEDATE "
            f"= ? WHERE Z_PK = ?",
            (previous_Z_OPT + 1, previous_ZMESSAGECOUNTER + 1, previous_ZLASTMESSAGE + 1, current_date, chat_id))

    # Currently not in use.
    def mention_everyone(self, chat_id):
        """
       Call get_members_by_chat_id(chat_id)
       Create a string called mention_string for each element in the list we get do the following:
       Append B Append the element
       Get the last message id in get_message_by_chat_id(chat_id)
       Edit that message in the db such that:
       ZTEXT would be @everyone and (Z_PK = last message id)
       Edit the row in messages_media_table where ZMESSAGE = last message id, Make ZMETADATA = mention_string
       """
        # Get members
        members = self.get_members_by_chat_id(chat_id)

        # Create mention string
        mention_string = ''.join(f'B{member}\n' for member in members)
        self.update_chat_session(chat_id)


    # Getting the messages from a chat of a specific type (for example: 46 = poll)
    def get_messages_by_chat_id_and_type(self, chat_id, message_type) -> List[Message]:
        """
       From messages_table take all Z_PK (ZCHATSESSION = chat_id, ZMESSAGETYPE = message_type) sort by ZMESSAGEDATE (low to high)
       Uses SQL query
       """
        self.cursor.execute(
            f"SELECT Z_PK FROM {Session.messages_table} WHERE ZCHATSESSION = ? AND ZMESSAGETYPE = ? ORDER BY ZMESSAGEDATE ASC",
            (chat_id, message_type))
        if message_type == message_types["POLL"]:
            return [Session.Poll(id=row[0], cursor=self.cursor) for row in self.cursor.fetchall()]
        else:
            return [Session.Message(id=row[0], cursor=self.cursor) for row in self.cursor.fetchall()]

    def sort_chat_by_date(self, chat_id):
        """
        From messages_table take all Z_PK (ZCHATSESSION = chat_id) sort by ZMESSAGEDATE (low to high).
        For each Z_PK set the message_table.ZSORT of it to be its index.
        """
        # Get all messages IDs sorted by date (low to high)
        self.cursor.execute(
            f"SELECT Z_PK FROM {Session.messages_table} WHERE ZCHATSESSION = ? ORDER BY ZMESSAGEDATE ASC", (chat_id,))
        messages = self.cursor.fetchall()
        length = len(messages)
        # Update each message's ZSORT field with its index
        for index, (message_id,) in enumerate(messages):
            self.cursor.execute(
                f"UPDATE {Session.messages_table} SET ZSORT = ? WHERE Z_PK = ?", (index, message_id))
        self.cursor.execute(f"UPDATE {Session.chats_table} SET ZMESSAGECOUNTER = ? WHERE Z_PK = ?", (length, chat_id))

        # Commit changes to the database
        self.conn.commit()
