import json
from datetime import date
import logging
from venv import logger


logger = logging.getLogger(__name__)  # to output logs to the console


'''This script defines functions for loading video data from a JSON file.
The main function, load_path(), reads a JSON file containing YouTube video data,
and returns the data as a Python object. It also includes error handling to log issues
with file access or JSON parsing.
The file path is constructed using the current date, following the format YT_data_YYYY-MM-DD.json.
This function is intended to be used in the data loading phase of the ETL process, 
where it will read the raw video data extracted from the YouTube API and prepare it for further processing and loading into the data warehouse.
'''
def  load_data():
    file_path = f"./data/YT_data_{date.today()}.json"

    try:
        logger.info(f"Processing file: YT_data_{date.today()}")
        with open(file_path, 'r',encoding='utf-8') as raw_data:
            data = json.load(raw_data)

        return data
    
    except FileNotFoundError:
        logger.error(f"File not found: {file_path}")
        raise
    except json.JSONDecodeError:
        logger.error(f"Error decoding JSON from file: {file_path}")
        raise
    
