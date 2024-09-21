import requests
import my_json_repository
import keys_loader
from my_logger import print_info, print_error
import utils
import csv_utils

API_KEY = keys_loader.load_private_key("google_places")

BASE_URL = 'https://maps.googleapis.com/maps/api/place/nearbysearch/json'
SEARCH_URL = 'https://maps.googleapis.com/maps/api/place/textsearch/json'
DETAILS_URL = 'https://maps.googleapis.com/maps/api/place/details/json'
AUTOCOMPLETE_URL = "https://maps.googleapis.com/maps/api/place/autocomplete/json"

    
########################################################
def get_place_coordinates(query):
    params = {
        'query': query,
        'key': API_KEY
    }
    
    response = requests.get(SEARCH_URL, params=params)
    data = response.json()
    
    if data['status'] == 'OK' and data['results']:
        # Extract the coordinates from the first result
        place = data['results'][0]
        location = place['geometry']['location']
        print_info(f"get_place_coordinates for {query} - latitude {location['lat']}, longitude {location['lng']}")
        return location['lat'], location['lng']
    else:
        return None, None

#######################################################
google_classification_types = {
    #    google    :  my-app
        'locality' : 'city', 
        'administrative_area_level_1' : 'district', 
        'administrative_area_level_2' : 'district', 
        'park' : 'attraction',
        'airport' : 'airport',
        'establishment' : 'attraction'  # this can be a park, tourist-attraction, spa, museum, etc..
        }
    
    
def get_place_classification(place_name, country, write_to_file = False):
    # Step 1: Autocomplete to get place_id
    # types = ['(regions)', 'geocode']
    
    if country in place_name:
        search_name = place_name
    else:
        search_name = f"{place_name}, {country}"
    
    # check if information exists in local DB. only if not call google API
    db_file_path = csv_utils.get_destinations_file_path(country)
    csv_utils.create_csv_file(db_file_path, csv_utils.destinations_columns) # will create only once

    row_info = csv_utils.get_row(db_file_path, "Name", place_name)
    if row_info:
        return row_info[1]
    
    params = {
        'input': search_name,
        'key': API_KEY
        # 'types': types[0],  # Focus on regions (cities, countries, districts)
    }
    response = requests.get(AUTOCOMPLETE_URL, params=params)
    predictions = response.json().get('predictions', [])

    return_type = 'unknown'
    
    if predictions:
        num_predictions = min(3, len(predictions))
        airport_id = -1

        for id in range(num_predictions):
            place_id = predictions[id]['place_id']
            types = predictions[id]['types']
            name = predictions[id]['description']
        
            for key, value in google_classification_types.items():
                if key in types:
                    app_type = value
                    break
            
            if id == 0:
                db_row = [place_name, app_type, place_id]
                csv_utils.update_or_append_row(db_file_path, db_row)
                return_type = app_type
            elif app_type == 'airport':  # save also airport info, if exists
                db_row = [name, app_type, place_id]
                csv_utils.update_or_append_row(db_file_path, db_row)
                
            print_info(f"get_place_details : name = {name} types = {types} ; class = {return_type}")
                                
        if write_to_file:
            file_name = f"{utils.sanitize_filename(place_name)}.json"
            file_path = utils.get_country_folder(country)
            my_json_repository.save_json_data(file_name, file_path, response.json())
                        
        return return_type
    
    return None

#############################################################
def get_place_details(place_id):
    params = {
        'place_id': place_id,
        'key': API_KEY,
    }
    response = requests.get(DETAILS_URL, params=params)
    place_details = response.json().get('result', {})

    print(place_details)


#######################################################
def get_places_near_attraction(attraction_name, place_type, country, write_to_file = False):
    # Geocoding to get the coordinates of the attraction
    # For simplicity, you might need to use another API or database to get coordinates based on the attraction name.

    # Example coordinates for demonstration purposes
    latitude, longitude = get_place_coordinates(attraction_name)
    if not latitude or not longitude:
        return None
    
    # Parameters for the Places API request
    params = {
        'key': API_KEY,
        'location': f'{latitude},{longitude}',
        'radius': 5000,  # Radius in meters
        'type': place_type  # 'restaurant' or 'lodging' (for hotels)
    }

    response = requests.get(BASE_URL, params=params)
    places = response.json()

    if write_to_file:
        file_name = utils.sanitize_filename(f"{attraction_name}-{place_type}.json")
        file_path = utils.get_country_folder(country)
        my_json_repository.save_json_data(file_name, file_path, places)
    
    return places['results']

####################################################################################
def get_hotel_details(place_id, country, write_to_file = False):
    params = {
        'place_id': place_id,
        'key': API_KEY
    }
    
    response = requests.get(DETAILS_URL, params=params)
    data = response.json()

    if data['status'] == 'OK':
        result = data['result']
        # save hotel details 
        if write_to_file:
            file_name = utils.sanitize_filename(f"{result.get('name')}.json")
            my_json_repository.save_json_data(f"{country}/{file_name}", data)
        
        return {
            'name': result.get('name'),
            'rating': result.get('rating'),
            'address': result.get('formatted_address'),
            'phone_number': result.get('formatted_phone_number'),
            'website': result.get('website'),
            'price_level': result.get('price_level'),
            'number_of_reviews': result.get('user_ratings_total'),
            'types': result.get('types')
        }
    return None


def search_for_hotels(query, country, write_to_file = False):
    params = {
        'query': query,  # Example: 'hotels near Zakopane, Poland'
        'type': 'lodging',  # This filters the search for hotels
        'key': API_KEY
    }
    
    response = requests.get(SEARCH_URL, params=params)
    data = response.json()
    
    hotels = []
    if data['status'] == 'OK':
        for result in data['results']:
            hotels.append({
                'name': result['name'],
                'place_id': result['place_id']
            })
        
        if write_to_file:
            file_name = utils.sanitize_filename(f"{query}-lodging.json")
            file_path = utils.get_country_folder(country)
            my_json_repository.save_json_data(file_name, file_path, data)       
             
    return hotels



######  The following are test examples for the functions in this file
def hotels_search_test(display_details = False):
    # Example usage
    country = "Poland"
    destination = 'hotels near Zakopane'
    hotels = search_for_hotels(destination, country, True)
    print(hotels)

    # Example usage
    if display_details:
        for hotel in hotels:
            details = get_hotel_details(hotel['place_id'], country, True)
            print(details)


def near_attraction_test():
    # Example usage
    country = "Poland"
    attraction = 'poprad' # 'Gubałówka Hill'
    restaurants = get_places_near_attraction(attraction, 'restaurant', country, True)
    hotels = get_places_near_attraction(attraction, 'lodging', country, True)

    print("Nearby Restaurants:")
    for place in restaurants:
        print(place['name'])

    print("\nNearby Hotels:")
    for place in hotels:
        print(place['name'])
        
        
def place_classification_test(place_name, country = None):
    if not country:
        country = utils.check_country_in_text(place_name)
    types = get_place_classification(place_name, country, True)
    # if place_id:
    #     get_place_details(place_id)
    print(f"Place Name {place_name}, {country} Place Types: {types}")


# hotels_search_test(True)
# place_classification_test("Lesser Poland", "poland")
# place_classification_test("wroclaw", "Poland")
# place_classification_test("Terma Bania", "Poland")
# place_classification_test("Tatra National Park", "Poland")
