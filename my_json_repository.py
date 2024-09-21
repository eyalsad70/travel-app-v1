import json
import keys_loader
import s3_repository
import os
from my_logger import print_info, print_error
import re

json_local_repository = True  # otherwise use AWS S3



# Example usage
# filename = "invalid, file name; test.txt"
# valid_filename = sanitize_filename(filename)
# print(valid_filename)  # Output: invalid--file-name--test.txt


def save_json_data(fileName, file_path, data):
    if fileName and data:
        file_path_name = f"{file_path}/{fileName}"
        if json_local_repository:
            with open(file_path_name, "w") as write_file:
                json.dump(data, write_file, indent=4)    
        else:
            s3_repository.upload_json_to_s3(data, file_path_name)
    else:
        print_error("save_json_data :: no fileName or no data attached")
        

def read_json_data(fileName, file_path):
    file_path_name = f"{file_path}/{fileName}"
    if not json_local_repository:
        result = s3_repository.download_s3_file(fileName, file_path_name)
    else:
        result = os.path.exists(file_path_name)
    
    if result == False:
        return None
    
    with open(file_path_name, "r") as read_file:
        data = json.load(read_file)
    # if file storage is S3 remove local file
    if not json_local_repository:
        os.remove(file_path_name)
    
    return data

           
