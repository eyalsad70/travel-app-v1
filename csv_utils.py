
""" 
    Utilities for CSV files operations - creation, read, save, find data, etc...
"""

# import pandas as pd
import csv 
import os
from my_logger import print_info, print_error
import utils

###############   TABLES Definitions    ##########################
attractions_columns = ['Name', 'Type', 'NearestCity', 'Latitude', 'Longitude', 'GoogleId']

def get_attractions_file_path(country):
    folder = utils.get_country_folder(country)
    if not folder.endswith('/'):
        folder += '/'
    return folder + 'attractions.csv'


destinations_columns = ["Name", "Type", "GoogleId", "Latitude", "longitude"]

def get_destinations_file_path(country):
    folder = utils.get_country_folder(country)
    if not folder.endswith('/'):
        folder += '/'
    return folder + 'destinations.csv'


ammenties_columns = ['Name', 'Type', 'Address', 'Rating', 'Reviews', 'Latitude', 'Longitude', 'GoogleId', "Url"]

def get_ammentis_file_path(country):
    folder = utils.get_country_folder(country)
    if not folder.endswith('/'):
        folder += '/'
    return folder + 'ammenties.csv'

################################################################################################
def create_csv_file(file_path, column_names):      
    if os.path.exists(file_path):  
        return -1
    
    with open(file_path, "w", newline='', encoding='utf-8') as fd:
        writer = csv.writer(fd)
        
        # add 1st line
        first_line = []
        for column in column_names:
            first_line.append(column)
        writer.writerow(first_line)
    return 0

####################################################
def get_row(file_path, column_name, column_value):
    if not os.path.exists(file_path):
        print("file not exists. you must create it first")
        return None
           
    with open(file_path, 'r', newline='', encoding='utf-8') as file:
        reader = csv.reader(file)
        headers = next(reader)  # Assume first row is header
        try:
            name_index = headers.index(column_name)  # Find the index of this column
        except:
            print_error(f"update_or_append_row : column {column_name} is not valid")
            return False
        
        rows = list(reader)
        
        # Check if name already exists
        for i, row in enumerate(rows):
            try:
                if row[name_index] == column_value:
                     return row
            except:
                print_error(f"file {file_path} has corrupted row {row}. skipping...")
                
    return None    
    
###############################################################################
def update_or_append_row(file_path, new_row, search_index = None):
    # search_index is the name of the column that is checked for existance. if exists replace it with new content. otherwise, append
    
    if not os.path.exists(file_path):
        print("file not exists. you must create it first")
        return False
        
    # Read existing data
    rows = []
    name_exists = False
    row_index = -1
    
    with open(file_path, 'r', newline='', encoding='utf-8') as file:
        reader = csv.reader(file)
        headers = next(reader)  # Assume first row is header
        if search_index:
            try:
                name_index = headers.index(search_index)  # Find the index of this column
            except:
                print_error(f"update_or_append_row : column {search_index} is not valid")
                return False
        else:
            name_index = 0
        
        new_name = new_row[name_index]
        rows = list(reader)
        
        # Check if name already exists
        if search_index:
            for i, row in enumerate(rows):
                if row[name_index] == new_name:
                    name_exists = True
                    row_index = i
                    break
    
    if name_exists:
        # Replace the existing row
        rows[row_index] = new_row
        print(f"Updated row for {new_name}")
    else:
        # Append the new row
        rows.append(new_row)
        print(f"Added new row for {new_name}")
    
    # Write all rows back to the file
    with open(file_path, 'w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(headers)  # Write the header row
        writer.writerows(rows)  # Write all data rows

    return True


def csv_test():
    locations_coordinates_file = "./data/locations.csv"
    locations_columns = ["Name", "Type", "Latitude", "Longitude"]

    lines = [ ["Zakopane waling street", "Urban", 17.6786655656, 32.343434], 
              ["high tatras pleso", "Nature", 18.43434, 31.75444], 
              ["warshaw aquapark", "Leisure", 22.555555, 45.665434] ]
    replaced_line = ["warshaw aquapark", "Leisure", 33.455555, 44.445434]
    wrong_column = "Title"
    
    create_csv_file(locations_coordinates_file, locations_columns)
    for line in lines:
        update_or_append_row(locations_coordinates_file, line, "Name")
    
    # test invalid request
    update_or_append_row(locations_coordinates_file, replaced_line, wrong_column)
    # update line
    update_or_append_row(locations_coordinates_file, replaced_line, "Name")
    
# df = pd.read_json("data.json")
# print(df)

# csv_test()

