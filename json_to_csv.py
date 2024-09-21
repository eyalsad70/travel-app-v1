import my_json_repository
import csv_utils
import re
import google_maps_api
import pandas as pd


filename = "zakopane--poland.json"

def create_locations_table_from_json(filename):
    data = my_json_repository.read_json_data(filename)
    if data:
        content = data["result"]
        # Split into a list of lines
        lines = content.splitlines()
        csv_utils.create_csv_file(csv_utils.locations_coordinates_file, csv_utils.locations_columns)
        
        for line in lines:
            print(line)
            # Check if the line starts with a numeric value and then split the rest of line
            match = re.match(r'^(\d+)\.\s*(.*)', line)
            if match:
                # Extract the number and the rest of the line
                number = match.group(1)  # The numeric value
                rest_of_line = match.group(2)  # The rest of the string after the number
                # Split the rest of the line based on ' - ' delimiter
                parts = rest_of_line.split(' - ')  
                csv_line = []
                place_name = parts[0]  # place name
                csv_line.append(place_name)
                csv_line.append(parts[1]) # place_type
                latitude, longitude = google_maps_api.get_place_coordinates(place_name)
                csv_line.append(latitude)
                csv_line.append(longitude)
                # print(number, place_name, place_type, latitude, longitude)
                csv_utils.update_or_append_row(csv_utils.locations_coordinates_file, csv_line)

try:
    df = pd.read_csv(".\data\locations.csv")   
    print(df)
except:
    pass
     
                    