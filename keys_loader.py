
""" 
Utilities for loading access-key/token/passwords required by this project
consumer of this APP MUST provide his own keys and set them as environment variables (see help.txt for instructions)
"""

import os
from my_logger import print_info, print_error

# PRIVATE_KEYS_FILE = "C:/Naya/Python projects/private-data.txt"
telebot_key = os.getenv('TELEGRAM_BOT_TOKEN')
if not telebot_key:
    print_error("environment keys were NOT set. please see help.txt to understand how to set")
    exit()

google_places_key = os.getenv('GOOGLE_PLACES_KEY')
rapid_api_key = os.getenv('RAPID_API_KEY')

aws_access_key = os.getenv('AWS_ACCESS_KEY_ID')
aws_secret_key = os.getenv('AWS_SECRET_ACCESS_KEY')

# site_key_name represnts the name given to the site key in private key file
my_secured_sites_key_names = {
# RapidAPI sites
        "openai" : rapid_api_key,
        "booking" : rapid_api_key,
        "ai_trip_planner" : rapid_api_key,  # optional - deprecated
        # Telegram Bot
        "telebot" : telebot_key,
        "telebot_id" : 6550133750,
        # AWS (optional - as local storage also available)- Has both key & secret ; they are treated as 2 "sites" for simplicity
        "aws_key" : aws_access_key,
        "aws_secret" : aws_secret_key,
        # the following allow access to OPenAI Apis directly and not though rapid
        "openai_direct" : 0,  # optional - deprecated
        # key for google maps api - to get locations, hotels, restaurants, etc...
        "google_places" : google_places_key
    }

aws_s3_bucket_name = 'eyalsad70-s3'
aws_s3_folder_name = 'my_travel_app_v1/'

#######################################################################################
def load_private_key(site_name):
    site = site_name.lower()
    if site not in my_secured_sites_key_names.keys():
        print_error(f"site_name {site_name} is NOT valid")
        return None
    
    return my_secured_sites_key_names[site]

    # with open(PRIVATE_KEYS_FILE, "r") as read_file:
    #     lines = read_file.readlines()
    #     for line in lines:
    #         if my_secured_sites_key_names[site] in line:
    #             # find ket offset in line assuming separator is '=' (with or without spaces)
    #             start_index = line.find('=') + 1
    #             if line[start_index] == ' ':
    #                 start_index += 1
    #             end_index = line.find("\n")
    #             if end_index > 0:
    #                 key = line[start_index:end_index]
    #             else:
    #                 key = line[start_index:]
    #             return key
    # return None
                
            

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


