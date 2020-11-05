import os
from datetime import date

from google.cloud import storage
from google.oauth2 import service_account


def upload_file(source_file_name, destination_blob_name, bucket_name='climateai_data_repository'):
    """Uploads a file to the bucket."""
    # bucket_name = "your-bucket-name"
    # source_file_name = "local/path/to/file"
    # destination_blob_name = "storage-object-name"

    try:
        credentials = service_account.Credentials.from_service_account_file(
            './climate-ai-data.json')
        storage_client = storage.Client(
            credentials=credentials, project='climate-ai')

        bucket = storage_client.bucket(bucket_name)
        blob = bucket.blob(destination_blob_name)

        blob.upload_from_filename(source_file_name)

        print(
            "File {} uploaded to {}.".format(
                source_file_name, destination_blob_name
            )
        )
    except Exception as err:
        print(
            "File {} failed to upload to {}. Error: {}".format(
                source_file_name, destination_blob_name, err
            )
        )


def download_file(source_blob_name, destination_file_name, bucket_name='climateai_data_repository'):
    """Downloads a file from the bucket."""
    # bucket_name = "your-bucket-name"
    # source_file_name = "local/path/to/file"
    # destination_blob_name = "storage-object-name"

    try:
        credentials = service_account.Credentials.from_service_account_file(
            './climate-ai-data.json')
        storage_client = storage.Client(
            credentials=credentials, project='climate-ai')

        bucket = storage_client.bucket(bucket_name)
        blob = bucket.blob(source_blob_name)
        blob.download_to_filename(destination_file_name)

        print(
            "Blob {} downloaded to {}.".format(
                source_blob_name, destination_file_name
            )
        )
    except Exception as err:
        print(
            "Blob {} failed to download to {}. Error: {}".format(
                source_blob_name, destination_file_name, err
            )
        )


def check_exist(blob_name, bucket_name='climateai_data_repository'):
    try:
        credentials = service_account.Credentials.from_service_account_file(
            './climate-ai-data.json')
        storage_client = storage.Client(
            credentials=credentials, project='climate-ai')

        bucket = storage_client.bucket(bucket_name)
        stats = storage.Blob(
            bucket=bucket, name=blob_name).exists(storage_client)
        return True if stats > 0 else False
    except Exception as err:
        print(
            "Failed to check blob {}. Error: {}".format(
                blob_name, err
            )
        )
        return False


def download_from_storage(file_name, blob_path, data_dir):
    """ Try to download from Google Storage """
    local_file_name = prepare_local_file_path(file_name, data_dir)
    if check_exist(blob_path):
        download_file(blob_path, local_file_name)
        print("Downloaded "+file_name+" from storage")
        return True
    else:
        print("Could not download "+blob_path+" from storage")
        return False


def prepare_local_file_path(file_name, data_dir):
    """ Create or get local file path """
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)
    return data_dir + "/" + file_name
