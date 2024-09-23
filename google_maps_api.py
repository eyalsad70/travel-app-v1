"""
Google Places API (supported through google cloud and requires acceess key created in google cloud) -
handlers to get locations, hotels, restuarnants, etc...
note that API is called only if data isn't in cache, 
and when called save results in cache (to reduce response-time & costs)
"""

import requests
import my_json_repository
import keys_loader
from my_logger import print_info, print_error
import utils
import csv_utils
import pandas as pd
import os
import re

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
        return location['lat'], location['lng'], place['place_id']
    else:
        return None, None, None

#####################################################################
def get_place_db_coordinates(place_name, file_path, country):
    latitude, longitude = None, None
    
    if not os.path.exists(file_path):  
        return None, None
    
    # check first in DB for coordinates
    df = pd.read_csv(file_path)
    if place_name in df['Name'].values:
        # Return the row where the 'Name' column matches the search name
        row = df.loc[df['Name'] == place_name]
        latitude = row['Latitude']
        longitude = row['Longitude']
    return latitude, longitude

#####################################################################
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
    updated = False
    
    df = pd.read_csv(db_file_path)

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
            
            if id == 0 or app_type == 'airport':
                if id == 0:
                    name_value = place_name
                    return_type = app_type
                else:
                    name_value = name
                
                if not df['Name'].isin([name_value]).any():
                    if place_id:
                        details = get_place_details(place_id)
                        location = details['geometry']['location']                
                        db_row = [name_value, app_type, place_id, location['lat'], location['lng']]
                    else:
                        db_row = [name_value, app_type, place_id, 0, 0]    
                    df.loc[len(df)] = db_row
                    updated = True

            print_info(f"get_place_details : name = {name} types = {types} ; class = {return_type}")
                                
        if write_to_file:
            file_name = f"{utils.sanitize_filename(place_name)}.json"
            my_json_repository.save_json_data(file_name, country, response.json())

        if updated:
            print(df)
            # Save the DataFrame to a CSV file
            df.to_csv(db_file_path, index=False, encoding='utf-8')                 
            
    return return_type
   

#############################################################
def get_place_details(place_id):
    params = {
        'place_id': place_id,
        'key': API_KEY,
    }
    response = requests.get(DETAILS_URL, params=params)
    place_details = response.json().get('result', {})

    # print(place_details)
    return place_details


#######################################################
def get_places_near_attraction(attraction_name, place_type, country, write_to_file = False):
    # Geocoding to get the coordinates of the attraction
    # For simplicity, you might need to use another API or database to get coordinates based on the attraction name.
   
    # check first in Destinations DB for coordinates
    db_file_path = csv_utils.get_destinations_file_path(country)
    latitude, longitude = get_place_db_coordinates(attraction_name, db_file_path, country)

    # check in attractions DB for coordinates
    if not latitude:
        db_file_path = csv_utils.get_attractions_file_path(country)
        latitude, longitude = get_place_db_coordinates(attraction_name, db_file_path, country)

    # Example coordinates for demonstration purposes
    if not latitude:
        latitude, longitude, place_id = get_place_coordinates(attraction_name)

    if not latitude or not longitude:
        return None

    return get_places_near_attraction_coordinates(latitude, longitude, place_type, country, attraction_name)

##########
def get_places_near_attraction_coordinates(latitude, longitude, place_type, country, file_name = None):
    # Parameters for the Places API request
    params = {
        'key': API_KEY,
        'location': f'{latitude},{longitude}',
        'radius': 5000,  # Radius in meters
        'type': place_type  # 'restaurant' or 'lodging' (for hotels)
    }

    response = requests.get(BASE_URL, params=params)
    if response.status_code == 200:
        places = response.json()

        if file_name:
            new_file_name = utils.sanitize_filename(f"{file_name}-{place_type}.json")
            my_json_repository.save_json_data(new_file_name, country, places)
        
        return places['results']
    return None

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
            my_json_repository.save_json_data(file_name, country, data)
        
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

##########################################################################################
def search_for_ammenties(query, country, place_type, write_to_file = False):
    places_types = {"lodging" : "hotels", 'restaurant' : 'restaurants'}
    
    places = []

    if place_type not in places_types.keys():
        print_error(f"Invalid place type {place_type}")
        return places
    
    # check if information exists in local DB. only if not call google API
    db_file_path = csv_utils.get_ammentis_file_path(country)
    csv_utils.create_csv_file(db_file_path, csv_utils.ammenties_columns) # will create only once
    
    df = pd.read_csv(db_file_path)
    updated = False

    file_name = utils.sanitize_filename(f"{query}-{place_type}.json")
    data = my_json_repository.read_json_data(file_name, country)
    
    if data:
        write_to_file = False
    else:
        search_query = f"{places_types[place_type]} near {query}, {country}"
    
        params = {
            'query': search_query, 
            'type': place_type,  # This filters the search for hotels
            'key': API_KEY
        }    
       
        response = requests.get(SEARCH_URL, params=params)
        if response.status_code != 200:
            return places
        
        data = response.json()
    
    if data['status'] == 'OK':
        if write_to_file:
            my_json_repository.save_json_data(file_name, country, data)     
            
        for result in data['results']:
            photos = result.get('photos', [])
            if len(photos) > 0 and 'html_attributions' in photos[0]:
                html_ref = f"{result['photos'][0]['html_attributions']}"
                url = re.search(r'href="(.*?)"', html_ref)
                # Check if a match is found
                if url:
                    url = url.group(1)
            else:
                url = 'none'
            
            address = result.get('formatted_address',[])
            if len(address) < 2:
                address = result.get('vicinity', 'No address available')
                
            # ammenties_columns = ['Name', 'Type', 'Address', 'Rating', 'Reviews', 'Latitude', 'Longitude', 'Google-Id', "Url"]
            new_row = {
                'Name' : result['name'],
                'Type' : place_type,
                'Address' : address,
                'Rating' : result.get('rating', 0),
                'Reviews' : result.get('user_ratings_total', 0),
                'Latitude' : result['geometry']['location']['lat'],
                'Longitude' : result['geometry']['location']['lng'],
                'Google-Id': result['place_id'],
                'Url' : url
            }
            places.append(new_row)          
            
            if not df['Name'].isin([new_row['Name']]).any():
                df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
                updated = True  
                
        if updated:
            print(df)
            # Save the DataFrame to a CSV file
            df.to_csv(db_file_path, index=False, encoding='utf-8')            
            
    return places


###############################################################################
######  The following are test examples for the functions in this file
###############################################################################
def hotels_search_test(display_details = False):
    # Example usage
    country = "Poland"
    destination = 'Zakopane'
    hotels = search_for_ammenties(destination, country, "lodging", True)
    print(hotels)

    # Example usage
    if display_details:
        for hotel in hotels:
            details = get_hotel_details(hotel['place_id'], country, True)
            print(details)


def near_attraction_test(destination, country):
    # Example usage
    restaurants = get_places_near_attraction(destination, 'restaurant', country, True)
    # hotels = get_places_near_attraction(destination, 'lodging', country, True)

    print("Nearby Restaurants:")
    for place in restaurants:
        print(place['name'])

    # print("\nNearby Hotels:")
    # for place in hotels:
    #     print(place['name'])
        
        
def place_classification_test(place_name, country = None):
    if not country:
        country = utils.check_country_in_text(place_name)
    types = get_place_classification(place_name, country, True)
    # if place_id:
    #     get_place_details(place_id)
    print(f"Place Name {place_name}, {country} Place Types: {types}")


# hotels_search_test(False)
# place_classification_test("Lesser Poland", "poland")
# place_classification_test("wroclaw", "Poland")
# place_classification_test("Terma Bania", "Poland")
# place_classification_test("Tatra National Park", "Poland")
# near_attraction_test('poprad', 'slovakia')
# near_attraction_test('zakopane', 'poland')