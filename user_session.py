""" 
This file define and hold user sessions.
each user that access this APP through telegram BOT on his mobile/desktop will have a session created 
for him with his details and activities 
This allows multiple users using the BOT simultanously without affecting each other 
"""

from my_logger import print_info, print_error
import bot_brain

class UserSession():
    def __init__(self, userId) -> None:
        self.user_id = userId
        self.bot_started = False
        self.countries_searched = []
        self.bot_activities = []
        self.email = ""
        self.bot_brain = bot_brain.BotBrain()


    def handle_user_message(self, message):
        if self.bot_started:
            self.log_activity(message.text, "request")
        content = self.bot_brain.handle_user_message(message)
        if content:
            self.log_activity(content, "response")
        return content

    
    def next_bot_action(self):
        return self.bot_brain.next_action()

    
    def start(self):
        self.bot_started = True
        self.bot_brain.restart()

    
    def get_bot_brain(self):
        return self.bot_brain

    
    def log_activity(self, message:str, message_from):
        self.bot_activities.append(f"{message_from}: {message}")

    
    def display_bot_activities(self):
        for activity in self.bot_activities:
            print(activity)

            
    def add_coutry(self, country:str):
        if not country in self.countries_searched:
            self.countries_searched.append(country)

    
    def serialize(self):  # convert all session content into a JSON format data (se we can save it in cache)
        data = dict()
        data['user_id'] = self.user_id
        data['countries'] = self.countries_searched
        data['activities'] = self.bot_activities
        data['email'] = self.email
        return data
        
    def save_activities_log(self):
        file_name = f"summary_{self.user_id}.txt"
        with open(file_name, "w") as fd:
            fd.write(self.bot_activities)
    
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


def display_users_activities():
    for user_obj in user_sessions.values():
        print(f"User Id {user_obj.user_id} email {user_obj.email} : has the following activities: ")
        user_obj.display_bot_activities()
        

