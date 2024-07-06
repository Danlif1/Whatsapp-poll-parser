#!/bin/bash


# Create a virtual environment
python3 -m venv myenv

# Activate the virtual environment
source myenv/bin/activate

# Download dependencies for Python
pip3 install json
pip3 install numpy
pip3 install openpyxl
pip3 install pandas
pip3 install gspread
pip3 install oauth2client
pip3 install google-api-python-client
pip3 install python-dotenv
pip3 install sqlite3
pip3 install typing
pip3 install datetime
pip3 install blackboxprotobuf
pip3 install hexdump



# Run main.py
python3 main.py
