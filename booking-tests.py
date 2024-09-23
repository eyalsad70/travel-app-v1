
""" 
    BOOKING.COM APIs through rapid API. it gives hotel realtime details info 
    it was tested but NOT used at the moment as it reuires real start/end dates. will be used in future for more detailed trip plan 
"""

import keys_loader
import rapidApi_client

file_name = "hotels_locations.json"
country = 'poland'
request_url = "/api/v1/hotels/searchDestination?query=wroclaw"
booking_host_url = "booking-com15.p.rapidapi.com"
booking_header = keys_loader.RapidApiRequestHeader(keys_loader.load_private_key("booking"), booking_host_url)

data = rapidApi_client.get_rapidApi_data(booking_header, request_url)
# data = rapidApi_client.read_json_data(file_name, country)

file_name = "hotels_wraclaw.json"
request_url = "/api/v1/hotels/getFilter" # ?dest_id=-537080&search_type=CITY&arrival_date=2024-10-15&departure_date=2024-10-18&adults=2&room_qty=1"

request_body = {
  "dest_id": "-537000",
  "search_type": "city",
  "arrival_date": "2024-10-15",
  "departure_date": "2024-10-18",
  "adults": 2,
  "room_qty": 1
  }

data = rapidApi_client.get_rapidApi_data(booking_header, request_url, request_body)
