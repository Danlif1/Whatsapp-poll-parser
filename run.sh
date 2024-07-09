#!/bin/bash


# Create a virtual environment
python3 -m venv venv

# Activate the virtual environment
source myenv/bin/activate

# Download dependencies for Python
pip3 install -r requirements.txt



# Run main.py
python3 main.py