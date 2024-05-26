import os

import pyautogui
import pyperclip
import time
import subprocess

from dotenv import load_dotenv


def open_whatsapp():
    subprocess.Popen(['open', '-a', 'WhatsApp'])


def search_chat(chat_name):
    time.sleep(2)
    pyautogui.keyDown('command')
    pyautogui.press('f')
    pyautogui.keyUp('command')
    time.sleep(1)
    pyperclip.copy(chat_name)
    pyautogui.hotkey('command', 'v')
    time.sleep(1)
    # Press Enter to search
    pyautogui.press('enter')
    time.sleep(1)
    pyautogui.press('down')
    pyautogui.press('down')
    pyautogui.press('space')
    time.sleep(1)
    pyautogui.keyDown('command')
    pyautogui.keyDown('shift')
    pyautogui.press('i')
    pyautogui.keyUp('command')
    pyautogui.keyUp('shift')
    time.sleep(1)
    # WARNING: might exit chat watch out keep sleeping long
    for i in range(1, 30):
        pyautogui.press('down')
    time.sleep(3)
    pyautogui.press('up')
    pyautogui.press('up')
    pyautogui.press('up')
    time.sleep(1)
    pyautogui.press('space')
    time.sleep(1)
    pyautogui.press('tab')
    pyautogui.press('tab')
    pyautogui.press('space')


def run_whatsapp_part():
    load_dotenv()
    chat_name = os.getenv('chat_name')
    open_whatsapp()
    search_chat(chat_name)


def exit_whatsapp_part():
    subprocess.Popen(['killall', 'WhatsApp'])
    time.sleep(2)
    open_whatsapp()
