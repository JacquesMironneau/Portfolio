from __future__ import print_function
import os.path

from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials


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
        print(folder)
        return folder.get('id')

creds = init_creds()
gdrive_api = build_grive_api()
