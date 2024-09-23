"""
Telegram BOT handlers
initialize the bot, listen on requests, and support responses through handlers
"""

import telebot
from telebot import types
import time, datetime
import requests
import json
import keys_loader
from my_logger import print_info, print_error
import user_session

test_token = keys_loader.load_private_key("telebot")
bot_name = "eyal_cde_test1"


# Get url for updates - run this once from Browser (not from here) to get chat id
# if you get empty list enter some text in the bot itself and
# bot_url_get_updates = f'https://api.telegram.org/bot{test_token}/getUpdates'
# print(bot_url_get_updates)

def send_welcome_message():
    # put your chat id and send a message
    bot_url = f'https://api.telegram.org/bot{test_token}/'
    chat_id = int(keys_loader.load_private_key("telebot_id"))

    current_time = time.localtime()
    time_string = time.strftime("%Y-%m-%d %H:%M:%S", current_time)


    text = f'Wake up!! Its {time_string}'
    url = bot_url + f'sendMessage?chat_id={chat_id}&text={text}'
    print(url)

    # # Print the get request
    resp = requests.get(url)
    print(resp.text)

    message = json.loads(resp.text)['result']
    print(message)

###################################################################################################

def log_message(message):
        print_info(f"Message ID: {message.message_id} From User ID: {message.from_user.id} ; Message Text: {message.text}")

# Create bot class
bot = telebot.TeleBot(test_token)

def start_bot():    
    # start listening
    bot.polling()
    

@bot.message_handler(commands=['start'])
def welcome(message):
    # get user session for this user. create it if not exists. Note that this 'start' command can be used also to restart session
    userSession = user_session.get_user_session(message.from_user.id, True)
    userSession.start()
    
    bot.reply_to(message, "welcome to my Travel BOT")
    # tbd - send picture
    with open('./data/welcome_photo.jpg', 'rb') as photo:
        bot.send_photo(message.from_user.id, photo)
    response = userSession.handle_user_message(message)
    bot.reply_to(message, response)
    


@bot.message_handler(content_types=['text'])
def handle_response(message):
   
    log_message(message)

    userSession = user_session.get_user_session(message.from_user.id)
    
    if userSession:        
        response = userSession.handle_user_message(message)
        if response:
            bot.reply_to(message, response)
        response = userSession.next_bot_action()
        if response:
            bot.reply_to(message, response)
    else:
        bot.reply_to(message, "press /start to begin!!")


# send_welcome_message()
