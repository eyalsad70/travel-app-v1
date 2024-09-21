
import re
import os

# A sample list of country names (could also be loaded from an external source)
countries = ["Israel", "Canada", "France", "Germany", "Slovakia", "Poland"]

# Join country names into a single regex pattern
pattern = r'\b(?:' + '|'.join(re.escape(country) for country in countries) + r')\b'


def sanitize_filename(filename):
    # Define a regex pattern to match any invalid characters
    # For this example, we'll replace anything that's not a word character (letters, digits, or underscore), a hyphen, or a dot.
    sanitized = re.sub(r'[^\w\.-]', '-', filename)
    return sanitized.lower()


def check_country_in_text(text):
    match = re.search(pattern, text.title())
    if match:
        return match.group()
    else:
        print("No valid country found, or country not supported by app.")
        return None


def detect_area(input_text):
    areas = ['north', 'south', 'east', 'west', 'center']
    detected_area = ""
    words = input_text.lower().split()
    for word in words:
        if word in areas:
            detected_area = detected_area  + word + ' '
    return detected_area


def create_country_folder(country:str):
    folder_path = f"./data/{country.lower()}"

    # Check if folder exists
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)        
        
def get_country_folder(country:str):
    return f"./data/{country.lower()}"


# Example
# text = "I want to visit south east poland and explore the beautiful landscapes."
# print(check_country_in_text(text))
# print(detect_area(text))

    