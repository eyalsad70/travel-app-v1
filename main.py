""" 
MAIN Handler of travel app project
"""

import my_bot
from my_logger import init_logger

if __name__ == "__main__":
    init_logger()
    my_bot.start_bot()