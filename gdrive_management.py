from __future__ import print_function
import os.path
import os
import io
import mimetypes

from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials

from googleapiclient.http import MediaIoBaseDownload, MediaFileUpload


# NOTE If scopes are modified you need to delete the file token.json
# TODO(thomas) allow users to enter their drive url or folder url on app first startup
SCOPES = ['https://www.googleapis.com/auth/drive']
PF_FOLDER_NAME = "portfolio_media"
PF_FOLDER_METADATA= {
    'name':PF_FOLDER_NAME,
    'mimeType':'application/vnd.google-apps.folder'
}

PF_FOLDER_ID = None



def init_creds():
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first time

    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)

    # If there are no (valid) credentials available, let the user log in
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port = 0)
        # Save the credentials for the next run
        with open('token.json','w') as token:
            token.write(creds.to_json())
    return creds


def build_grive_api():
    return build('drive', 'v3', credentials=creds)



def getFolder():
    response = gdrive_api.files().list(q="name='"+ PF_FOLDER_NAME +"'",
                            spaces='drive',
                            fields="nextPageToken, files(id, name)",
                            pageToken=None).execute()

    folder = response.get('files',[])[0]
    if not folder:
        # We create the folder named portfolio_media in the drive

        f = gdrive_api.files().create(body=PF_FOLDER_METADATA, fields='id').execute()
        print("folder created")
        return f.get('id')
    else:
        return folder.get('id')


"""
download the images stored on the google drive folder
to the path entered

:param str path: the path where the files will be downloaded to
"""
def download_projects_images(path):
    images = getImages()
    if not images:
        print (f"No files found in {PF_FOLDER_NAME}")
    else:
        for img in images:
            req = gdrive_api.files().get_media(fileId=img.get('id'))
            file_header = io.BytesIO()
            downloader = MediaIoBaseDownload(file_header, req)
            done = False
            while not done:
                status, done = downloader.next_chunk()
                print(f"Downloading file {img.get('name')} from google drive [{int(status.progress() * 100):2d}%]")
            with open(path+'/'+img.get('name'), "wb") as f:
                f.write(file_header.getbuffer())

"""
get The images from the google drive folder
"""
def getImages():
    response = gdrive_api.files().list(q="'" + getFolder() + "' in parents",
                                    spaces='drive',
                                    fields='nextPageToken, files(id, name)',
                                    pageToken = None).execute()
    return response.get('files',[])


def uploadImageToDriveFolder(filename):
    # creating the file metadata to add it to the google drive folder
    file_md = {
        'name':filename,
        'parents': [getFolder()]
    }

    # path of the file on the server
    filepath = 'static/upload/' + filename
    # building the media metadata
    media = MediaFileUpload(filepath,
                            mimetype=mimetypes.guess_type(filename)[0])
    # uploading the file to the google drive folder
    file = gdrive_api.files().create(body=file_md,
                                        media_body=media,
                                        fields='id').execute()
    print(f"File added : {file} to {PF_FOLDER_NAME}")



if os.environ.get('CREDS'):
    with open("credentials.json","w") as credentials:
        credentials.write(os.environ.get('CREDS'))



creds = init_creds()
gdrive_api = build_grive_api()
