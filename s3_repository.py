import boto3
import json
import keys_loader
from botocore.exceptions import ClientError
from my_logger import print_info, print_error

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
s3_buket_name = keys_loader.aws_s3_bucket_name
s3_root_folder = keys_loader.aws_s3_folder_name

def upload_json_to_s3(json_content, s3_file_name):
    try:
        # Convert JSON content to string
        json_data = json.dumps(json_content)

        # Upload the JSON string as an object to S3
        s3.put_object(Bucket=s3_buket_name, Key=s3_root_folder + s3_file_name, Body=json_data)

        print_info(f"File '{s3_file_name}' successfully uploaded to '{s3_buket_name}'")
    except Exception as e:
        print_error(f"Error uploading file to S3: {e}")


def download_s3_file(file_key, download_path):
    try:        
        # Check if the file exists by fetching the object metadata
        s3.head_object(Bucket=s3_buket_name, Key=file_key)
        print_info(f"File '{file_key}' exists in bucket '{s3_buket_name}'.")

        # If it exists, download the file
        s3.download_file(s3_buket_name, file_key, download_path)
        print_info(f"File '{file_key}' has been downloaded to '{download_path}'.")
        return True
    
    except ClientError as e:
        # If the error is a 404, the file does not exist
        if e.response['Error']['Code'] == '404':
            print_error(f"File '{file_key}' does not exist in bucket '{s3_buket_name}'.")
        else:
            # Something else went wrong
            print_error(f"An error occurred: {e}")
        return False


def upload_file_to_s3(s3_file_key, local_file_path):
    # Upload the file
    try:
        s3.upload_file(local_file_path, s3_buket_name, s3_file_key)
        print_info(f"File {local_file_path} uploaded successfully to s3://{s3_buket_name}/{s3_file_key}")
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

    # Specify your S3 bucket and the file name to be created in the bucket
    s3_file_name = 'tourist_locations_new.json'
    download_path = f"./data/{s3_file_name}"

    # Upload the JSON content to the specified S3 bucket
    upload_json_to_s3(json_content, s3_file_name)

    download_s3_file(s3_root_folder + s3_file_name, download_path)


# s3_internal_test()