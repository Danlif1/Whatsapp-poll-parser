import os

import pyautogui
import pyperclip
import time
import subprocess

from dotenv import load_dotenv


# Opening whatsapp.
def open_whatsapp():
    subprocess.Popen(['open', '-a', 'WhatsApp'])


# Searching for the chat.
def search_chat(chat_name):
    # Waiting for whatsapp to open.
    time.sleep(2)
    # Searching for a chat.
    pyautogui.keyDown('command')
    pyautogui.press('f')
    pyautogui.keyUp('command')
    time.sleep(1)
    # Entering chat name.
    pyperclip.copy(chat_name)
    pyautogui.hotkey('command', 'v')
    time.sleep(1)
    # Searching.
    pyautogui.press('enter')
    time.sleep(1)
    # Going to the first option (first down do nothing) and entering the chat.
    pyautogui.press('down')
    pyautogui.press('down')
    pyautogui.press('space')
    time.sleep(1)
    # Opening chat info.
    pyautogui.keyDown('command')
    pyautogui.keyDown('shift')
    pyautogui.press('i')
    pyautogui.keyUp('command')
    pyautogui.keyUp('shift')
    time.sleep(1)
    # WARNING: might exit chat watch out keep sleeping long
    # Going all the way down.
    for i in range(1, 30):
        pyautogui.press('down')
    # Waiting for safety.
    time.sleep(3)
    # Going 3 up (Export chat).
    pyautogui.press('up')
    pyautogui.press('up')
    pyautogui.press('up')
    time.sleep(1)
    # Exporting chat.
    pyautogui.press('space')
    time.sleep(1)
    # Choosing without media.
    pyautogui.press('tab')
    pyautogui.press('tab')
    pyautogui.press('space')


def run_whatsapp_part():
    load_dotenv()
    chat_name = os.getenv('chat_name')
    open_whatsapp()
    search_chat(chat_name)


# Exiting whatsapp
def exit_whatsapp_part():
    subprocess.Popen(['killall', 'WhatsApp'])
    time.sleep(2)
    open_whatsapp()
