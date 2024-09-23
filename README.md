# Whatsapp poll parser
Transferring polls from WhatsApp to Google Sheets

## How to select chat, Google Sheets path, SQLite database path, and actual people names.
You need to use a .env file, this is the format:
```
chat_name = "The name of the chat you want to use"
sheet_id = "In the URL of the google sheets this is what comes after /d/"
path_to_db = "/Users/$USER/Library/Group\ Containers/group.net.whatsapp.WhatsApp.shared/ChatStorage.sqlite"
people_map = '{"phoneNumber1": "name1 (This is how you want him to be called)", "phoneNumber2": "name2"}'
runner = "Your name"
```
## How to run
You need to use run.sh, write this into the terminal:
```
./run.sh
```
If it doesn't work it means you need to permit it, run the following:
```
chmod +x run.sh
./run.sh
```

## Common errors
### Can't transfer the polls from Excel to Google Sheets
Create a Google Cloud services account (Look up [https://console.cloud.google.com](https://console.cloud.google.com))

Connect it to your Google Sheet with an editor status

Copy and paste the credentials.json file into the folder where you run the code.

Rerun


## What the code do?

### initialize people function:
This will load the people_map from the .env file
### translate_data function:
This code will take the data we got from ZRECEIPTINFO and will translate it to the stuff we need.
### turn_off/on_wifi, force_quit_whatsapp, open_whatsapp functions:
Currently useless was meant to be used for a different project.
### Session class:
This will hold all the stuff that we need to query the whatsapp database.
### __init__ (for Session) function:
Gets the path to the whatsapp database and connect to it.
### Chat class:
Holds all the data about a certain class:
### __init__ (for Class) function:
Gets the class id and saves it.
### Message class:
Holds all the data about a single message.
### __init (for Message) function:
Gets the message id and the cursor (How we interact with the database) and saves them.
### get_time (for Message) function:
Query the database for the time of the message and parse it.
### get_sender (for Message) function:
Query the database for the sender of the message (The default namem, not the one saved on your phone or the person_map)
### get_content (for Message) function:
Query the database for the text of the message.
### Poll class (an extension of message):
A poll is a message in whatsapp of type 46.
### __init__ (for Poll) function:
Same as __init for Message.
### get_info (for poll) function:
If you want raw it will return you the bytes of the poll data.

If you don't want it raw it will return you a map with the following:
```
{
    'header': 'header of the poll',
    'options': ['option1', 'option2',...],
    'votes': [int_votes1, int_votes2,...]
}
```
### get_chat_id (for Session) function:
Given the chat name (from the .env file), it will return you the chat id.
### get_messages_by_chat_id (for Session) function:
Given the chat id, it will return you the id of every message in a chat.
### get_members_by_chat_id (for Session) function:
Given the chat id, it will return you the tokens of every member in a group (looks like this: [phoneNumber]@whatsapp...)
### mention_everyone (for Session) function:
Currently useless it was meant for a different project.
### get_messages_by_chat_id_and_type (for Session) function:
Given a chat id and a message type, return all the ids for messages of that type.
### extract_polls function:
Given a chat name return all the polls in a list parsed to a readable format (maps).
### extract_poll_data function:
Given a chat name, convert all the formats of the polls from maps to lists to fit the excel.
### create_sheet function:
Given all the polls in a list of lists, create an Excel sheet holding that data.
### calculate_color function:
Given the maximal value of a row, the minimal value of a row, and the current value of a cell, calculate its color.
### hex_to_rgb function:
Given the hexadecimal color value convert it to the rgb format.
### transfer_sheet function:
After creating the Excel sheet, transfer it to the Google sheet, Given the Excel sheet name, and the Google sheet id.
### main function:
Load the .env file and call all the functions.
### split_custom_pattern function:
Was used to create the headers of every column in the Excel sheet.
