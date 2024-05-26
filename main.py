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

# parse whatsapp chat.
def extract_poll_data(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        lines = file.readlines()

    poll_started = False
    poll_name = None
    poll_number = 1
    all_polls = [
        ['', 'יוצר הסקר', 'תאריך הסקר', 'כותרת הסקר', 'אופציה 1', 'מספר עונים על 1', 'אופציה 2', 'מספר עונים על 2',
         'אופציה 3', 'מספר עונים על 3', 'אופציה 4', 'מספר עונים על 4', 'אופציה 5', 'מספר עונים על 5', 'אופציה 6',
         'מספר עונים על 6', 'אופציה 7', 'מספר עונים על 7', 'אופציה 8', 'מספר עונים על 8', 'אופציה 9', 'מספר עונים על 9',
         'אופציה 10', 'מספר עונים על 10', 'אופציה 11', 'מספר עונים על 11', 'אופציה 12', 'מספר עונים על 12',
         'תאריך בדיקה אחרון', 'בודק אחרון']]
    single_poll = [poll_number]
    for line in lines:
        if "POLL:" in line:
            match = re.match(r'\[(\d{2}/\d{2}/\d{4}), (\d{1,2}:\d{2}:\d{2})\] (.*?):', line)
            if match:
                date = match.group(1)
                time = match.group(2)
                name = match.group(3)
                if name == "Daniel Lifshitz":
                    name = "דניאל סודי"
                datetime_str = f"{date} {time}"
                name = name.split()[0]

                datetime_obj = datetime.strptime(datetime_str, "%d/%m/%Y %H:%M:%S")

                abs_time = datetime_obj.strftime("%-d.%-m.%y %H:%M")
                single_poll.append(name)
                single_poll.append(abs_time)
            poll_started = True
            continue

        if poll_started:
            if not poll_name:
                poll_name = line.strip()
                single_poll.append(poll_name)
            else:
                match = re.search(r'OPTION: (.+) \((\d+) vote[s]?\)', line)
                if match:
                    option = match.group(1)
                    votes = int(match.group(2))
                    single_poll.append(option)
                    single_poll.append(votes)
                else:
                    current_time = datetime.now().strftime("%-d.%-m.%y %H:%M")
                    single_poll.append(current_time)
                    single_poll.append("דניאל")
                    all_polls.append(single_poll)
                    poll_number += 1
                    single_poll = [poll_number]
                    poll_name = None
                    poll_started = False

    return all_polls



# Create the excel sheet.
def create_sheet(poll_data):
    wb = openpyxl.Workbook()
    ws = wb.active

    font = openpyxl.styles.Font(name='Arial', size=13)
    thin_border = Border(left=Side(style='thin'),
                         right=Side(style='thin'),
                         top=Side(style='thin'),
                         bottom=Side(style='thin'))
    first = 1
    for row_index, data_list in enumerate(poll_data, start=1):
        for i in range(0, 30):
            cell = ws.cell(row=row_index, column=i + 1)
            cell.border = thin_border
            cell.alignment = Alignment(horizontal='left', vertical='bottom', text_rotation=180)
        if first:
            length = len(data_list)
            for i in range(0, length):
                cell = ws.cell(row=row_index, column=i + 1, value=data_list[i])
                cell.border = thin_border
                cell.font = font
            first = 0
            continue
        length = len(data_list)

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

        ws.cell(row=row_index, column=29, value=data_list[-2]).font = font
        ws.cell(row=row_index, column=30, value=data_list[-1]).font = font

    wb.save("poll_data.xlsx")


# color all votes.
def calculate_color(min_value, max_value, value):
    ratio = (value - min_value) / (max_value - min_value)
    r = int((222 - 35) * (1 - ratio)) + 35
    g = int((239 - 158) * (1 - ratio)) + 158
    b = int((245 - 208) * (1 - ratio)) + 208
    return f'{r:02x}{g:02x}{b:02x}'



# transfer from excel to google sheet.
def transfer_sheet(from_name, to_name):
    excel_file = from_name
    sheet_id = to_name

    scope = ['https://spreadsheets.google.com/feeds',
             'https://www.googleapis.com/auth/drive']
    credentials = ServiceAccountCredentials.from_json_keyfile_name('credentials.json', scope)
    client = gspread.authorize(credentials)

    df = pd.read_excel(excel_file)
    df.replace([np.inf, -np.inf], '', inplace=True)
    df.fillna('', inplace=True)

    sheet = client.open_by_key(sheet_id)
    worksheet = sheet.get_worksheet(0)
    data = df.values.tolist()
    worksheet.update('A2', data)


def main():
    load_dotenv()
    zip_name = os.getenv("zip_name")
    enter_whatsapp.run_whatsapp_part()
    time.sleep(5)
    move_from_downloads_to_here.moving_file(zip_name)
    file_path = '_chat.txt'
    poll_data = extract_poll_data(file_path)
    create_sheet(poll_data)
    transfer_sheet("poll_data.xlsx", "1UkqRW1LlgwcQMlK8zV0E8mkw990QqiRNquo69F5dHUM")
    move_from_downloads_to_here.remove_files(zip_name)
    enter_whatsapp.exit_whatsapp_part()


if __name__ == "__main__":
    main()



# For the title

# def split_custom_pattern(s):
#     words = s.split()
#     result = []
#     pattern = [2, 2, 2, 2, 4, 2, 4, 2, 4, 2, 4, 2, 4, 2, 4, 2, 4, 2, 4, 2, 4, 2, 4, 2, 4, 2, 4, 3, 2]
#     index = 0
#     pattern_index = 0
#
#     while index < len(words):
#         # Determine the current group size based on the pattern
#         group_size = pattern[pattern_index % len(pattern)]
#         # Create a group of words based on the current group size
#         group = words[index:index + group_size]
#         # Join the group into a single string and add to the result list
#         result.append(' '.join(group))
#         # Move the index forward by the size of the current group
#         index += group_size
#         # Move to the next pattern
#         pattern_index += 1
#
#     return result
#
#
# # Example usage
# variable = "יוצר הסקר	תאריך הסקר	כותרת הסקר	אופציה 1	מספר עונים על 1	אופציה 2	מספר עונים על 2	אופציה 3	מספר עונים על 3	אופציה 4	מספר עונים על 4	אופציה 5	מספר עונים על 5	אופציה 6	מספר עונים על 6	אופציה 7	מספר עונים על 7	אופציה 8	מספר עונים על 8	אופציה 9	מספר עונים על 9	אופציה 10	מספר עונים על 10	אופציה 11	מספר עונים על 11	אופציה 12	מספר עונים על 12	תאריך בדיקה אחרון	בודק אחרון"
# print(split_custom_pattern(variable))
