
import os
from my_logger import print_info, print_error

####  The following Data represnts the names of keys and tokens used in this project and saved in a private file (which isn't part of this project
####  real access keys & tokens should be achieved by the project user, and saved in a file at your will

PRIVATE_KEYS_FILE = "C:/Naya/Python projects/private-data.txt"

# site_key_name represnts the name given to the site key in private key file
my_secured_sites_key_names = {
    # RapidAPI sites
    "openai" : "openAI_key",
    "booking" : "booking_key",
    "ai_trip_planner" : "aiTripPlanner_key",
    # Telegram Bot
    "telebot" : "telebot_token",
    "telebot_id" : "telebot_chat_id",
    # AWS - Has both key & secret ; they are treated as 2 "sites" for simplicity
    "aws_key" : "aws_access_key_id",
    "aws_secret" : "aws_secret_access_key",
    # the following allow access to OPenAI Apis directly and not though rapid
    "openai_direct" : "openAI_direct_key",
    # key for google maps api - to get locations, hotels, restaurants, etc...
    "google_places" : "google_places_api_key"
}

aws_s3_bucket_name = 'eyalsad70-s3'
aws_s3_folder_name = 'my_travel_app_v1/'

#######################################################################################
def load_private_key(site_name):
    site = site_name.lower()
    if site not in my_secured_sites_key_names.keys():
        print_error(f"site_name {site_name} is NOT valid")
        return None
    
    with open(PRIVATE_KEYS_FILE, "r") as read_file:
        lines = read_file.readlines()
        for line in lines:
            if my_secured_sites_key_names[site] in line:
                # find ket offset in line assuming separator is '=' (with or without spaces)
                start_index = line.find('=') + 1
                if line[start_index] == ' ':
                    start_index += 1
                end_index = line.find("\n")
                if end_index > 0:
                    key = line[start_index:end_index]
                else:
                    key = line[start_index:]
                return key
    return None
                
            

class RapidApiRequestHeader:
    def __init__(self, key, url) -> None:
        self.headers = { 'x-rapidapi-key': key, 
                         'x-rapidapi-host': url,
                         'Content-Type': 'application/json'
        }
    def getKey(self):
        return self.headers['x-rapidapi-key']
    def getUrl(self):
        return self.headers['x-rapidapi-host']
    

# key = load_private_key("telebot")
# print(key)
# key = load_private_key("aws_secret")
# print(key)


