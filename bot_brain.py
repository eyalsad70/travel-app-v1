
import json
import keys_loader
from my_logger import print_info, print_error
import user_session
import utils
import my_openai
import google_maps_api

###################################################################################################

class BotBrain():
    """ This class holds the travel-app BOT brains with all supported actions and requests/responses logic
    
    THE BOT is currently support the following operations:
    command /start - to start/restart bot session for user 
    text requests:
        select a country
        select destination (in selected country) - destination can be a city, region-name, or an area (i.e. north east, central, etc...)
            - user will receive a list of attractions
        select hotels - if user didn't choose a city he will be prompts for major cities in the area and can choose a city
        select restaurants
        get summary in mail 
"""
    
    user_action_state_machine = {
        # 'state' : "next suggestion for user"
        'start' :'please select a country',
        'country_sel' : 'please select destination (can be a city, region-name, or an area (i.e. north east, central))',
        'destination_sel' : "\n",
        # 'city_sel' : 'please select city from list',  # this state is optional and only if user choose non-city destination
        # 'hotel_sel' : 'please select hotel from list',
        # 'rest_sel' : 'please select restaurant',
        'summary_sel' : 'please insert your email address'
    }
    
    menu = """ 
            menu-options (choose number):
                1. find tourist attractions
                2. find nearby hotels
                3. find nearby restaurants 
                5. email summary
            """
    
    
    def __init__(self) -> None:
        self.start_command = 'start'
        self.restart()
        
    def restart(self):
        self.action_state = 'start'
        self.started = False
        self.last_country_selected = ""
        self.last_destination_selected = ""
        self.tmp_city_names = []
    
    # ---------------------------------------------------------------------
    def handle_user_message(self, message):
        """ 
            this method is the Bot brain which handles the state machine and create proper responses to user 
        """
        if self.action_state == 'start':
            # handle country selection
            if self.started:
                result = self.handle_country_selection(message)
                if result: 
                    self.action_state = 'country_sel'
                    # self.response_sent = False
                    return self.user_action_state_machine['country_sel']
                else:
                    # self.response_sent = True
                    return f"Invalid country selected. choose again"
            else:
                self.started = True
                return self.user_action_state_machine['start']
            
        elif self.action_state == 'country_sel':
            # handle destination selection
            result = self.handle_destination_selection(message)   
            if result: 
                self.action_state = 'destination_sel'
                return self.user_action_state_machine['destination_sel']
            else:
                return f"destination is not valid or not of proper type for {self.last_country_selected}. choose again"     
            

        elif self.action_state == 'destination_sel':
            # if self.response_sent:    
            #     result = self.handle_destination_selection(message)   
            #     if result: 
            #         self.action_state = 'destination_sel'
            #         self.response_sent = False
            #         return self.user_action_state_machine['destination_sel']
            #     else:
            #         return f"destination selected doesn't exists in country {self.last_country_selected}. choose again"     
            # else:
            
            # need to check user response -> attractions(1), hotels(2), restaurants(3) and activate proper handler
            request = message.text
            if '1' in request:
                content = self.get_attractions()
            elif '2' in request:
                content = self.get_nearest_hotels()
            return content
    
    
    def next_action(self):
        if self.action_state == 'destination_sel':
            return self.menu
        return None

    
    def handle_country_selection(self, message):
        country = utils.check_country_in_text(message.text)  
        if country:
            # create folder for raw data if required
            utils.create_country_folder(country)
            # create db-table name / new-csv-file if required
            userSession = user_session.get_user_session(message.from_user.id)
            userSession.add_coutry(country)
            self.last_country_selected = country
            return True
        else:
            return False

            
    def handle_destination_selection(self, message):
        # should find attractions near by and return list in text format
        # if destination not a city will also fetch major cities in the area
        destination_name = message.text
        area = utils.detect_area(destination_name)
        if not area:
            area = google_maps_api.get_place_classification(destination_name, self.last_country_selected, True)
        if area != "unknown":
            self.last_destination_selected = message.text
            return True
        return False
    

    def get_attractions(self):
        return my_openai.get_proccessed_content(self.last_destination_selected, 'attractions', self.last_country_selected)
        
        
    def get_nearest_cities(self):
        return None
        
    def get_nearest_hotels(self):
        return None
    
