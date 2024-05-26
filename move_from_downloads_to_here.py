import shutil
import os
import zipfile

# Moving the zip from downloads to . and extracting the file from it.
def moving_file(zip_name):
    # Getting the path to the zip.
    downloads_folder = os.path.expanduser("~/Downloads")
    destination_folder = os.getcwd()
    # Joining the entire path.
    source_path = os.path.join(downloads_folder, zip_name)
    # Setting the path to the destination.
    destination_path = os.path.join(destination_folder, zip_name)

    # Moving the zip.
    shutil.move(source_path, destination_path)

    # Extracting the file from the zip.
    with zipfile.ZipFile(zip_name, 'r') as zip_ref:
        zip_ref.extractall()

# Removing the zip and the txt file.
def remove_files(zip_name):
    os.remove(zip_name)
    os.remove('_chat.txt')
