"""
LOGGER 
"""
import logging

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
