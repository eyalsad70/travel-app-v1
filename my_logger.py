"""
LOGGER 
"""
import logging
import os
DOCKER_MODE = os.getenv('DOCKER_MODE')

# Configure logging to write to a file
def init_logger():
    logging.basicConfig(filename='logger.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def just_print(message:str):
    print(message)
    return 0

    
def print_info(message:str):
    # Log messages will be written to 'logger.log'
    logging.info(message)
    just_print(message)

def print_warning(message:str):
    # Log messages will be written to 'logger.log'
    logging.warning(message)
    just_print(message)

def print_error(message:str):
    # Log messages will be written to 'logger.log'
    logging.error(message)
    just_print(message)

# Walk through the current directory and its subdirectories
def test_file_integrity():  # used in docker only to test all files existance
    if DOCKER_MODE:
        for root, dirs, files in os.walk('.'):
            print(f"Directory: {root}")
            for file in files:
                print(f"  File: {file}")
        # Get the list of files and directories in the current directory
        # items = os.listdir('.')
        # # Print each item, specifying whether it's a file or a directory
        # for item in items:
        #     if os.path.isfile(item):
        #         print(f"File: {item}")
        #     elif os.path.isdir(item):
        #         print(f"Directory: {item}")
        