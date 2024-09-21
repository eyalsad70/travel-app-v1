import requests
import json 
import keys_loader
import os
from my_logger import print_info, print_error
import my_json_repository
import utils
import csv_utils

def query_prompt(place, country):
    prompt = f"List up to 15 tourist attractions in {place}, {country}. For each attraction, include only the name and type (e.g., urban, nature, historical) without any additional information"
    # prompt = f"List up to 15 tourist attractions in {place}. For each attraction, include the type of attraction (urban, nature, historical, etc.)."
    # prompt = f"I am looking for tourist attractions in {place}. I want up to 15 nature, urban and aqua-park attractions"
    return prompt

def classification_promt(place):
    prompt = f"""The user has entered the following location: {place}. Classify this location as a 'city', 'country', 'district', or 'region'. """
    return prompt

def nearest_cities_prompt(place, country):
    prompt = f"what are the biggest cities in {place}, {country}?. please state up to 3 cities"
    return prompt

    
def create_attractions_db(country):
    csv_utils.create_csv_file(csv_utils.get_attractions_file_path(country), csv_utils.attractions_columns)
    
    
def get_openai_content(prompt):
    """ Get LLM Content for OPEN-AI Query. return answer with content answer result in json format """
    
    url = "https://chatgpt-42.p.rapidapi.com/conversationgpt4-2"


    payload = {
        "messages": [
            {
                "role": "system", "content": "You are a helpful travel assistant.",
                "role": "user",	"content": f"{prompt}"
            }
        ],
        "system_prompt": "",
        "temperature": 0.5,
        "top_k": 5,
        "top_p": 0.9,
        "max_tokens": 512,
        "web_access": False
    }

    private_key = keys_loader.load_private_key("openai")
    openai_header = keys_loader.RapidApiRequestHeader(private_key, "chatgpt-42.p.rapidapi.com")
    
    headers = {
        "x-rapidapi-key": f"{private_key}",
        "x-rapidapi-host": "chatgpt-42.p.rapidapi.com",
        "Content-Type": "application/json"
    }

    response = requests.post(url, json=payload, headers=headers)

    log_message = f"get_openai_content :  request {prompt} was sent. response code = {response.status_code}"
    
    if response.status_code == 200:
        print_info(log_message)

        # Convert the response to a Python dictionary (from JSON format)
        json_data = response.json()

        # print(json_data)
        return json_data

    print_error(log_message)
    return None

    
def get_keywords_from_openai(content):
    data = get_openai_content(f"Extract the key words from this content: {content}")
    return data



def get_proccessed_content(destination, content_type = 'attractions', country = None):
    ### its recommanded (but not mandatory) to specify the country for deterministic results
    if not country:
        country = utils.check_country_in_text(destination)
    
    if not country:
        print_error("get_proccessed_content -> can't find country in query. json file can't be saved")
        return None
    
    file_name = utils.sanitize_filename(destination) + f"-{content_type}" + ".json"
    file_path = utils.get_country_folder(country)
    json_data = my_json_repository.read_json_data(file_name, file_path)
    
    if not json_data:       # get data through OpenAI and save it
        prompt = query_prompt(destination, country)
        json_data = get_openai_content(prompt)
        if json_data:
            my_json_repository.save_json_data(file_name, file_path, json_data)
        else:
            return None            
                       
    content = json_data["result"]
        
    # Decode the Unicode-escaped string
    decoded_text = content #.encode('utf-8').decode('unicode_escape')
    
    # Split into a list of lines
    lines = decoded_text.splitlines()
    
    for line in lines:
        if len(line) > 5:
           print(line)
            
    return decoded_text

   
# json_data = get_openai_content(classification_promt("poprad"))
# json_data = get_openai_content(classification_promt("south west poland"))

def openAi_test():
    countries = ["Slovakia", "poland"]
    for country in countries:
        utils.create_country_folder(country)
    lines = get_proccessed_content("Poprad", 'attractions', countries[0])
    lines = get_proccessed_content("zakopane", 'attractions', countries[1])

# openAi_test()
       
    
