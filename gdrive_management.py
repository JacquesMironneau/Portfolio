from __future__ import print_function
import os.path
import os
import io
import mimetypes
from flask.globals import request

from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials

from googleapiclient.http import MediaIoBaseDownload, MediaFileUpload

# constants / global variables for gdrive
# NOTE If scopes are modified you need to delete the file token.json
SCOPES = ['https://www.googleapis.com/auth/drive']
PF_FOLDER_NAME = "portfolio_media"
PF_FOLDER_ID = None
PF_FOLDER_METADATA= {
    'name':PF_FOLDER_NAME,
    'mimeType':'application/vnd.google-apps.folder'
}

#upload_folder = os.path.join(, app.config['UPLOAD_FOLDER'])

def init_creds():
    """
        Inits the credentials for a google drive application,
        in order to store project's thumbnail on a google drive folder,
        dedicated to the portfolio
    """
    if os.environ.get('CREDS'):
        with open(os.path.join(os.path.abspath(os.path.dirname(__file__)),"credentials.json"),"w") as credentials:
            credentials.write(os.environ.get('CREDS'))
            print(os.environ.get('CREDS'), flush=True)

    if os.environ.get('DRIVE_TOKEN'):
        with open('token.json','w') as token:
            token.write(os.environ.get('DRIVE_TOKEN'))
            print(os.environ.get('DRIVE_TOKEN'), flush=True)

            


    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first time

    if os.path.exists(os.path.join(os.path.abspath(os.path.dirname(__file__)),'token.json')):
        creds = Credentials.from_authorized_user_file(os.path.join(os.path.abspath(os.path.dirname(__file__)),'token.json'), SCOPES)

    # If there are no (valid) credentials available, let the user log in
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                os.path.join(os.path.abspath(os.path.dirname(__file__)),'credentials.json'), SCOPES)
            creds = flow.run_local_server(port = 0)
        # Save the credentials for the next run
        with open(os.path.join(os.path.abspath(os.path.dirname(__file__)),'token.json'),'w') as token:
            token.write(creds.to_json())
    return creds


def build_grive_api():
    """
        Returns an object that we use to call the api
    """
    return build('drive', 'v3', credentials=creds)


def getFolder():
    """
        Get the Id of the folder stored on google drive

        :return str id: the id of the folder where images are stored on google drive
    """
    # NOTE(thomas) we prolly should make the request first, and then execute it in a separate line
    # We create the request to find the folder named portfolio_media
    request = gdrive_api.files().list(q="name='"+ PF_FOLDER_NAME +"'",
                            spaces='drive',
                            fields="nextPageToken, files(id, name)",
                            pageToken=None).execute()

    # check if there is a folder with that name
    if len(request.get('files',[])) > 0:
        # It exist so we return it's id
        folder = request.get('files',[])[0].get('id')
        return folder
    else:
        # We create the folder named portfolio_media in the drive
        f = gdrive_api.files().create(body=PF_FOLDER_METADATA, fields='id').execute()
        print("folder created")
        return f.get('id')


def download_projects_images(path):
    """
        Downloads the images stored on the google drive folder,
        to a given path

        :param str path: the path where the files will be downloaded to
    """
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


            if not os.path.exists(path):
                os.makedirs(path)
                print(f" {path} created", flush=True)

            with open(os.path.join(path,img.get('name')), "wb") as f:
                f.write(file_header.getbuffer())

def getImages():
    """
        Get the images stored on the google drive folder

        :return Object ids: a list of images ids stored in the google drive folder
    """
    response = gdrive_api.files().list(q="'" + getFolder() + "' in parents",
                                    spaces='drive',
                                    fields='nextPageToken, files(id, name)',
                                    pageToken = None).execute()
    return response.get('files',[])


def uploadImageToDriveFolder(filename):
    """
        Upload a given image to the drive folder

        :param str filename: the name of the file we want to upload
    """
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




creds = init_creds()
gdrive_api = build_grive_api()