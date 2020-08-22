from google.cloud import storage
import os

def upload(filename):
    # uploads a file to google filestorage and deletes it from the server and finally returns the file's url
    client = storage.Client.from_service_account_json('apply-ai-firebase-adminsdk.json')
    bucket = client.get_bucket('apply-ai-resumes')
    blob = bucket.blob(filename)
    blob.upload_from_filename('uploads/' + filename)
    os.remove('uploads/' + filename)
    return blob.public_url
