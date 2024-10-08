
"""
Utilities for JSON format files
json files contain raw data returned by API calls to openai/google/booking and other sites used by this project 
files repository can be local or remote (S3)
"""

import json
import keys_loader
import s3_repository
import os
from my_logger import print_info, print_error
import utils

json_local_repository = True  # otherwise use AWS S3
remove_local_file_when_loading_from_s3 = False


# Example usage
# filename = "invalid, file name; test.txt"
# valid_filename = sanitize_filename(filename)
# print(valid_filename)  # Output: invalid--file-name--test.txt


def save_json_data(fileName, country, data):
    if fileName and data:
        if json_local_repository:
            file_path_name = utils.get_country_folder(country) + fileName
            with open(file_path_name, "w") as write_file:
                json.dump(data, write_file, indent=4)    
        else:
            s3_repository.upload_json_to_s3(data, fileName, country)
    else:
        print_error("save_json_data :: no fileName or no data attached")
        

def read_json_data(fileName, country):
    file_path_name = utils.get_country_folder(country) + fileName

    if not json_local_repository:
        # downloa remote file into local storage
        result = s3_repository.download_s3_file(fileName, country)
    else:
        result = os.path.exists(file_path_name)
    
    if result == False:
        return None
    
    with open(file_path_name, "r") as read_file:
        data = json.load(read_file)
    # if file storage is S3 remove local file
    if remove_local_file_when_loading_from_s3 and not json_local_repository:
        os.remove(file_path_name)
    
    return data

           
