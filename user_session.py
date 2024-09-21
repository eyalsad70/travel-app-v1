""" This file define and hold user sessions.
    each user that access this APP through his BOT client will have a session created for him with his details and activities """

from my_logger import print_info, print_error
import bot_brain

class UserSession():
    def __init__(self, userId) -> None:
        self.user_id = userId
        self.bot_started = False
        self.countries_searched = []
        self.last_country_selected = ""
        self.last_location_selected = ""
        self.bot_activities = []
        self.email = ""
        self.bot_brain = bot_brain.BotBrain()

    def handle_user_message(self, message):
        if self.bot_started:
            self.log_activity(message)
        return self.bot_brain.handle_user_message(message)
    
    def next_bot_action(self):
        return self.bot_brain.next_action()
    
    def start(self):
        self.bot_started = True
        self.bot_brain.restart()
    
    def get_bot_brain(self):
        return self.bot_brain
    
    def log_activity(self, message:str):
        self.bot_activities.append(message)
    
    def add_coutry(self, country:str):
        if not country in self.countries_searched:
            self.countries_searched.append(country)
        self.last_country_selected = country
    
    def add_location(self, location):
        self.last_location_selected = location
        
    def serialize(self):  # convert all session content into a JSON format data (se we can save it in cache)
        data = dict()
        data['user_id'] = self.user_id
        data['countries'] = self.countries_searched
        data['activities'] = self.bot_activities
        data['email'] = self.email
        return data
        
        
user_sessions = dict()

def get_user_session(user_id, create_if_not_exists = False):
    session = None
    try:  # if session exists return its object ; otherwise create new one
        session = user_sessions[user_id]        
    except:
        if create_if_not_exists:
            session = UserSession(user_id)
            user_sessions[user_id] = session
            print_info(f"new user session was created for user {user_id}")
            
    return session

