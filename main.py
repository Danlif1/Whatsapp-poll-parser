import re
from datetime import datetime

import numpy as np
import openpyxl
from openpyxl.styles import Font, PatternFill, Border, Side, Alignment
import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials

import move_from_downloads_to_here
import enter_whatsapp
import time
from dotenv import load_dotenv
import os


# Parse whatsapp chat.
def extract_poll_data(file_path):
    # Moving the file to lines
    with open(file_path, 'r', encoding='utf-8') as file:
        lines = file.readlines()

    poll_started = False
    poll_name = None
    poll_number = 1

    # Every line in the polls excel,
    # first line isn't from whatsapp and is the title of each column,
    # see commented code to see how to generate (bottom of the page).
    all_polls = [
        ['', 'יוצר הסקר', 'תאריך הסקר', 'כותרת הסקר', 'אופציה 1', 'מספר עונים על 1', 'אופציה 2', 'מספר עונים על 2',
         'אופציה 3', 'מספר עונים על 3', 'אופציה 4', 'מספר עונים על 4', 'אופציה 5', 'מספר עונים על 5', 'אופציה 6',
         'מספר עונים על 6', 'אופציה 7', 'מספר עונים על 7', 'אופציה 8', 'מספר עונים על 8', 'אופציה 9', 'מספר עונים על 9',
         'אופציה 10', 'מספר עונים על 10', 'אופציה 11', 'מספר עונים על 11', 'אופציה 12', 'מספר עונים על 12',
         'תאריך בדיקה אחרון', 'בודק אחרון']]
    # Every parsed poll starts with the poll number.
    single_poll = [poll_number]
    # Going over each line in the chat.
    for line in lines:
        # "POLL:" means the start of a poll
        if "POLL:" in line:
            # We want the date, time, and name (2,2,4 = date, 2,2,2 or 1,2,2 = time .*? = name (stops at :))
            match = re.match(r'\[(\d{2}/\d{2}/\d{4}), (\d{1,2}:\d{2}:\d{2})\] (.*?):', line)
            if match:
                date = match.group(1)
                time = match.group(2)
                name = match.group(3)
                # If it's me it changes it into hebrew to keep it the same across all names (the names have two words)
                if name == "Daniel Lifshitz":
                    name = "דניאל סודי"
                # Combining the date and time to be one string.
                datetime_str = f"{date} {time}"
                # Taking the first word from each name (first name).
                name = name.split()[0]
                # Converting the date and time string into an object for parsing later.
                datetime_obj = datetime.strptime(datetime_str, "%d/%m/%Y %H:%M:%S")
                # Parsing the date and time object into my format.
                abs_time = datetime_obj.strftime("%-d.%-m.%y %H:%M")
                # Adding the name and time into the poll data.
                single_poll.append(name)
                single_poll.append(abs_time)
            # Starting to read the poll.
            poll_started = True
            continue

        if poll_started:
            # First line after the poll is the title of the poll.
            if not poll_name:
                poll_name = line.strip()
                # Adding the poll title into the poll data.
                single_poll.append(poll_name)
            else:
                # After the poll title we have the poll options in this format.
                match = re.search(r'OPTION: (.+) \((\d+) vote[s]?\)', line)
                if match:
                    # Adding the poll option and its votes into the poll data.
                    option = match.group(1)
                    votes = int(match.group(2))
                    single_poll.append(option)
                    single_poll.append(votes)
                else:
                    # If not match was found we reached the end of the poll,
                    # I now want to add that I added it to the Excel in the current time.
                    current_time = datetime.now().strftime("%-d.%-m.%y %H:%M")
                    single_poll.append(current_time)
                    single_poll.append("דניאל")
                    # Adding the full poll into the all polls variable.
                    all_polls.append(single_poll)
                    # Resetting the single_poll variable, and all other needed variables.
                    poll_number += 1
                    single_poll = [poll_number]
                    poll_name = None
                    poll_started = False
    return all_polls


# Create the Excel sheet.
def create_sheet(poll_data):
    wb = openpyxl.Workbook()
    ws = wb.active

    # Setting the font and border of each cell.
    # (13 in Excel = 10 in google sheets, thin border in Excel = border in google sheets)
    font = openpyxl.styles.Font(name='Arial', size=13)
    thin_border = Border(left=Side(style='thin'),
                         right=Side(style='thin'),
                         top=Side(style='thin'),
                         bottom=Side(style='thin'))
    first = 1
    for row_index, data_list in enumerate(poll_data, start=1):
        # For each cell in the row (we have 30 cells in each row),
        # we want to update the font and border (and alignment).
        for i in range(0, 30):
            cell = ws.cell(row=row_index, column=i + 1)
            cell.border = thin_border
            cell.alignment = Alignment(horizontal='left', vertical='bottom', text_rotation=180)
        # If it's the first line we want to add it as normal.
        if first:
            length = len(data_list)
            for i in range(0, length):
                cell = ws.cell(row=row_index, column=i + 1, value=data_list[i])
                cell.border = thin_border
                cell.font = font
            first = 0
            continue
        length = len(data_list)
        # Otherwise we do something a little different.
        for i in range(0, length - 2):
            cell = ws.cell(row=row_index, column=i + 1, value=data_list[i])
            cell.border = thin_border
            cell.font = font
            if i % 2 != 0 and 5 <= i <= len(data_list):
                value = float(data_list[i])
                min_value = min(float(val) for val in data_list[5:len(data_list) - 2:2])
                max_value = max(float(val) for val in data_list[5:len(data_list) - 2:2])
                color = calculate_color(min_value, max_value, value)
                cell.fill = PatternFill(start_color=color, end_color=color, fill_type='solid')
        # The last two cells are for the date of the update and the person who updated.
        ws.cell(row=row_index, column=29, value=data_list[-2]).font = font
        ws.cell(row=row_index, column=30, value=data_list[-1]).font = font

    wb.save("poll_data.xlsx")


# color all votes.
def calculate_color(min_value, max_value, value):
    # 222,239,245 is the maximum color,
    # 35,158,208 is the minimum color.
    ratio = (value - min_value) / (max_value - min_value)
    r = int((222 - 35) * (1 - ratio)) + 35
    g = int((239 - 158) * (1 - ratio)) + 158
    b = int((245 - 208) * (1 - ratio)) + 208
    return f'{r:02x}{g:02x}{b:02x}'


# transfer from excel to google sheet.
def transfer_sheet(from_name, to_name):
    # The name of the Excel file.
    excel_file = from_name
    # The id of the Google sheet.
    sheet_id = to_name

    # Credentials stuff.
    scope = ['https://spreadsheets.google.com/feeds',
             'https://www.googleapis.com/auth/drive']
    credentials = ServiceAccountCredentials.from_json_keyfile_name('credentials.json', scope)
    client = gspread.authorize(credentials)

    # Copying the Excel.
    df = pd.read_excel(excel_file)
    df.replace([np.inf, -np.inf], '', inplace=True)
    df.fillna('', inplace=True)

    # Updating the Google sheet.
    sheet = client.open_by_key(sheet_id)
    worksheet = sheet.get_worksheet(0)
    data = df.values.tolist()
    worksheet.update('A2', data)


def main():
    # loading env.
    load_dotenv()
    zip_name = os.getenv("zip_name")
    sheet_id = os.getenv("sheet_id")
    # Opening whatsapp and downloading chat.
    enter_whatsapp.run_whatsapp_part()
    # Waiting for whatsapp part to finish.
    time.sleep(5)
    # Moving it to the python directory and unzipping.
    move_from_downloads_to_here.moving_file(zip_name)
    file_path = '_chat.txt'
    # Creating Google sheet.
    poll_data = extract_poll_data(file_path)
    create_sheet(poll_data)
    transfer_sheet("poll_data.xlsx", sheet_id)
    # Resetting all data.
    move_from_downloads_to_here.remove_files(zip_name)
    enter_whatsapp.exit_whatsapp_part()


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
# variable = "יוצר הסקר	תאריך הסקר	כותרת הסקר	אופציה 1	מספר עונים על 1	אופציה 2	מספר עונים על 2	אופציה 3	מספר עונים על 3	אופציה 4	מספר עונים על 4	אופציה 5	מספר עונים על 5	אופציה 6	מספר עונים על 6	אופציה 7	מספר עונים על 7	אופציה 8	מספר עונים על 8	אופציה 9	מספר עונים על 9	אופציה 10	מספר עונים על 10	אופציה 11	מספר עונים על 11	אופציה 12	מספר עונים על 12	תאריך בדיקה אחרון	בודק אחרון"
# print(split_custom_pattern(variable))
