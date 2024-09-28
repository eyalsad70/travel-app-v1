""" 
MAIN Handler of travel app project
"""
import my_bot
from my_logger import init_logger, test_file_integrity
# from keys_loader import init_keys



if __name__ == "__main__":
    init_logger()
    # test_file_integrity()
 #   init_keys()
    
    my_bot.start_bot()