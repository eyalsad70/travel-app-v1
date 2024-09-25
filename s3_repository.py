
""" 
utilities for accessing AWS S3 buckets for saving/reading files
S3 can be used to save raw data returned by API calls to openai/google/booking and other sites used by this project
note that access token must be provided 
"""

import boto3
import json
import keys_loader
from botocore.exceptions import ClientError
from my_logger import print_info, print_error, print_warning
import utils

s3_bucket_name = 'eyalsad70-s3'
s3_root_folder = 'my_travel_app_v1/'


# Initialize a session using Amazon S3
def initialize_s3_client():
    key = keys_loader.load_private_key("aws_key")
    secret = keys_loader.load_private_key("aws_secret")

    s3 = boto3.client(
        's3',
        aws_access_key_id=key,
        aws_secret_access_key=secret,
        region_name='eu-central-1'  # Optional but recommended
    )
    return s3


s3 = initialize_s3_client()


# Function to check if a folder (prefix) exists in S3 and create it if not
def create_folder_if_not_exists(relative_folder):
    # Add a trailing slash to the folder name if it doesn't have one
    if not relative_folder.endswith('/'):
        relative_folder += '/'
    
    folder_name = f"{s3_root_folder}{relative_folder}"
    
    # Check if the folder exists by listing objects with the prefix
    response = s3.list_objects_v2(Bucket=s3_bucket_name, Prefix=folder_name, Delimiter='/')

    # Check if any objects/folders with the given prefix exist
    if 'Contents' not in response:
        print_info(f"Folder '{folder_name}' does not exist. Creating it...")
        # Create an empty object with the folder prefix
        try:
            s3.put_object(Bucket=s3_bucket_name, Key=folder_name)
            print_info(f"Folder '{folder_name}' created successfully!")
        except Exception as e:
            print_error(f"Error creating folder to S3: {e}")
            return False
    # else:
    #     print(f"Folder '{folder_name}' already exists.")
    return True
    
## ---------------------------------------------------------------------------------------
def upload_json_to_s3(json_content, s3_file_name, relative_folder):
    """
        s3_file_name - file name only (not path)
        relative_folder - folder to put file in, relative to project home folder 's3_root_folder'
    """
    if not relative_folder.endswith('/'):
        relative_folder += '/'
        
    try:
        # Convert JSON content to string
        json_data = json.dumps(json_content)

        # Upload the JSON string as an object to S3
        file_key = f"{s3_root_folder}{relative_folder}{s3_file_name}"
        s3.put_object(Bucket=s3_bucket_name, Key=file_key, Body=json_data)

        print_info(f"File '{file_key}' successfully uploaded to '{s3_bucket_name}'")
    except Exception as e:
        print_error(f"Error uploading file to S3: {e}")

# ------------------------------------------------------------------------------------------
def download_s3_file(file_name, relative_folder):
    """
    download file from S3 relative_folder into local repository (under same 'relative_folder' and name)
    """
    download_path = utils.get_country_folder(relative_folder) + file_name
    
    if not relative_folder.endswith('/'):
        relative_folder += '/'
        
    file_key = f"{s3_root_folder}{relative_folder}{file_name}"

    try:        
        # Check if the file exists by fetching the object metadata
        s3.head_object(Bucket=s3_bucket_name, Key=file_key)
        print_info(f"File '{file_key}' exists in bucket '{s3_bucket_name}'.")

        # If it exists, download the file
        s3.download_file(s3_bucket_name, file_key, download_path)
        print_info(f"File '{file_key}' has been downloaded to '{download_path}'.")
        return True
    
    except ClientError as e:
        # If the error is a 404, the file does not exist
        if e.response['Error']['Code'] == '404':
            print_warning(f"File '{file_key}' does not exist in bucket '{s3_bucket_name}'.")
        else:
            # Something else went wrong
            print_error(f"An error occurred: {e}")
        return False

### -------------------------------------------------------------------------------------
def upload_file_to_s3(file_name, relative_folder):
    # Upload the file
        
    download_path = utils.get_country_folder(relative_folder) + file_name
    
    if not relative_folder.endswith('/'):
        relative_folder += '/'
    
    file_key = f"{s3_root_folder}{relative_folder}{file_name}"

    try:
        s3.upload_file(download_path, s3_bucket_name, file_key)
        print_info(f"File {download_path} uploaded successfully to s3://{s3_bucket_name}/{file_key}")
    except Exception as e:
        print_info(f"Error uploading file: {e}")


######################################################################################

def s3_internal_test():
# Example JSON content
    json_content = {
        'tourist_locations': [
            {'name': 'Eiffel Tower', 'location': 'Paris, France'},
            {'name': 'Statue of Liberty', 'location': 'New York, USA'}
        ]
    }
    country = 'france'
    
    # Specify your S3 bucket and the file name to be created in the bucket
    s3_file_name = 'tourist_locations_new.json'

    status = create_folder_if_not_exists(country)
    if status:    
        # Upload the JSON content to the specified S3 bucket
        upload_json_to_s3(json_content, s3_file_name, country)

        utils.create_country_folder(country)
        download_s3_file(s3_file_name, country)


# s3_internal_test()