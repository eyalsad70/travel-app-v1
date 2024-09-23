""" 
RAPID-API HTTP Client adapter
"""

import http.client
import json
import keys_loader
from my_logger import print_info, print_error



def get_rapidApi_data(headers:keys_loader.RapidApiRequestHeader, request_str, request_body = None):
    conn = http.client.HTTPSConnection(headers.getUrl())

    if request_body:
        json_payload = json.dumps(request_body)
        conn.request("GET", request_str, json_payload, headers=headers.headers)
    else:
        conn.request("GET", request_str, headers=headers.headers)

    response = conn.getresponse()
    
    # Check if the request was successful (status code 200)
    if response.status == 200:
        print_info(f"rapidApi request {request_str} was sent. response code = {response.status}")
        # Read the response data
        data = response.read().decode('utf-8')

        # Convert the response to a Python dictionary (from JSON format)
        json_data = json.loads(data)
    
        return json_data
    else:
        print_error(f"rapidApi request {request_str} was sent. response code = {response.status}")

    
    

