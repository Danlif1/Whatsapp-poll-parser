import shutil
import os
import zipfile


def moving_file(zip_name):
    downloads_folder = os.path.expanduser("~/Downloads")
    file_to_move = zip_name
    destination_folder = os.getcwd()  # This gets the current working directory

    source_path = os.path.join(downloads_folder, file_to_move)
    destination_path = os.path.join(destination_folder, file_to_move)

    shutil.move(source_path, destination_path)

    with zipfile.ZipFile(zip_name, 'r') as zip_ref:
        zip_ref.extractall()

def remove_files(zip_name):
    os.remove(zip_name)
    os.remove('_chat.txt')

