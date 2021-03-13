from __future__ import print_function
import os.path
import os
import io
import mimetypes
from flask.globals import request
from models import db, Project

from app import ALLOWED_EXTENSIONS

from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials

from googleapiclient.http import MediaIoBaseDownload, MediaFileUpload

import gendrivetoken

class Storage():
    """
        Abstract class parent of every kind of storage
        If you want to add a cloud/storage provider simply derive this 
        @see SelfStorage or GdriveSyncStorage
    """
    def upload(self, file, filename): 
        pass

    def delete(self, image_name):
        pass

    def update(self, old_thumbnail, new_thumbnail):
        pass
    
    def allowed_files(self, filename: str) -> bool:
        """
            Checks if the extension of a given is allowed
        """
        return '.' in filename and \
            filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
  

    def __repr__(self):
        pass
    
    def __str__(self):
        return ""
    
class SelfStorage(Storage):

    def __init__(self, upload_folder):
        self.upload_folder = upload_folder

    def upload(self, file, filename): 
        """
            Upload a given image to the server

            :param bytes file : the binary file we will save on the server
            :param str filename: the name of the file we want to save on the server
        """
        if not os.path.exists(self.upload_folder):
            os.makedirs(self.upload_folder)
        file.save(os.path.join(self.upload_folder, filename))
        print(f"Add file : {filename} in server files", flush=True)

    
    def delete(self, image_name):
        try:
            os.remove(os.path.join(self.upload_folder, image_name))
            print(f"Deleted file : {image_name} from server files", flush=True)
        except:
            print(f"File: {image_name} doesn't exist in server files", flush=True)
            self.__clean_useless_files()
            
    def update(self, old_thumbnail, new_thumbnail):
        self.delete(old_thumbnail)
        self.upload(new_thumbnail, new_thumbnail.filename)
        print(f"Update file : from {old_thumbnail} to  {new_thumbnail.filename} in server files", flush=True)

    def __clean_useless_files(self):
        existing_images = [project.project_thumbnail for project in db.session.query(Project).all()]
        for file in os.listdir(self.upload_folder):
            if not file in existing_images:
               os.remove(os.path.join(self.upload_folder, file))
               print(f'Delete {file} as it is no longer used')


class GdriveSyncStorage(Storage):
    """
        Storage class using google drive API
        This uses the local storage for buffering and google drive
        for persistent data storage
    """

    SCOPES = gendrivetoken.SCOPES
    PF_FOLDER_NAME = "portfolio_media"
    PF_FOLDER_ID = None
    PF_FOLDER_METADATA = {
        'name': PF_FOLDER_NAME,
        'mimeType':'application/vnd.google-apps.folder'
    }


    def __init__(self, upload_folder):
        """
            Instanciate the Gdrive storage: set up the path
            then generate credentials, build the api and download the images
        """
        self.current_dir = os.path.abspath(os.path.dirname(__file__))
        self.token_path = os.path.join(self.current_dir,'token.json')
        self.creds_path = os.path.join(self.current_dir, 'credentials.json')
        self.server_storage = SelfStorage(upload_folder)

        self.creds = self.__init_creds()
        self.api= self.__build_api()

        self.drive_folder = self.__getFolder()
        
        self.download_projects_images(upload_folder)

    def upload(self, file, filename): # uploadImageToDriveFolder(filename)
        """
            Upload a given image to the server and then the drive folder

            :param str filename: the name of the file we want to upload
        """
        # Saving file to the server
        self.server_storage.upload(file, filename)

        # creating the file metadata to add it to the google drive folder
        file_md = {
            'name':filename,
            'parents': [self.drive_folder]
        }

        # path of the file on the server
        filepath = f'static/upload/{filename}'
        # building the media metadata
        media = MediaFileUpload(filepath,
                                mimetype=mimetypes.guess_type(filename)[0])
        # uploading the file to the google drive folder
        file = self.api.files().create(body=file_md,
                                            media_body=media,
                                            fields='id').execute()
        print(f"File added : {file} to {self.PF_FOLDER_NAME}")
    
    def delete(self, image_name):
        for img in self.getImages():
            if img.get('name') == image_name:
                self.api.files().delete(fileId = img.get('id')).execute()
                print(f"Deleted file : {image_name} from google drive", flush=True)
        
        self.server_storage.delete(image_name)

    def update(self, old_thumbnail_path, new_thumbnail):
        """
            Update an image (or thumbnail) by deleting the old one, and
            adding the new one

        """
        # First delete
        self.delete(old_thumbnail_path)
        self.server_storage.delete(old_thumbnail_path)
        # Then upload the new content
        self.upload(new_thumbnail,new_thumbnail.filename)
        print(f"Update file : from {old_thumbnail_path} to  {new_thumbnail.filename} in google drive", flush=True)


    def __init_creds(self):
        """
            Inits the credentials for a google drive application,
            in order to store project's thumbnail on a google drive folder,
            dedicated to the portfolio
        """
        if os.environ.get('CREDS'):
            with open(self.creds_path,"w") as credentials:
                credentials.write(os.environ.get('CREDS'))
                print('Getting data from CREDS env var', flush=True)

        if os.environ.get('DRIVE_TOKEN'):
            with open(self.token_path,'w') as token:
                token.write(os.environ.get('DRIVE_TOKEN'))
                print('Getting data from DRIVE_TOKEN env var', flush=True)

        creds = None
        # The file token.json stores the user's access and refresh tokens, and is
        # created automatically when the authorization flow completes for the first time

        if os.path.exists(self.token_path):
            creds = Credentials.from_authorized_user_file(self.token_path, self.SCOPES)

        return gendrivetoken.genTokenFromCreds(creds)

    def __build_api(self):
        """
            Returns an object that we use to call the api
        """
        return build('drive', 'v3', credentials = self.creds)

    # TODO refactor: maybe add folder in attribute, check if we need to get it each time or not
    def __getFolder(self):
        """
            Get the Id of the folder stored on google drive

            :return str id: the id of the folder where images are stored on google drive
        """
        # NOTE(thomas) we prolly should make the request first, and then execute it in a separate line
        # We create the request to find the folder named portfolio_media
        request = self.api.files().list(q="name='"+ self.PF_FOLDER_NAME +"'",
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
            f = self.api.files().create(body=self.PF_FOLDER_METADATA, fields='id').execute()
            print("folder created")
            return f.get('id')

    def getImages(self):
        """
            Get the images stored on the google drive folder

            :return Object ids: a list of images ids stored in the google drive folder
        """
        response = self.api.files().list(q="'" + self.drive_folder + "' in parents",
                                        spaces='drive',
                                        fields='nextPageToken, files(id, name)',
                                        pageToken = None).execute()
        return response.get('files',[])

    def download_projects_images(self, path):
        """
            Downloads the images stored on the google drive folder,
            to a given path

            :param str path: the path where the files will be downloaded to
        """
        images = self.getImages()
        if not images:
            print (f"No files found in {self.PF_FOLDER_NAME}", flush=True)
        else:
            for img in images:
                req = self.api.files().get_media(fileId=img.get('id'))
                file_header = io.BytesIO()
                downloader = MediaIoBaseDownload(file_header, req)
                done = False
                while not done:
                    status, done = downloader.next_chunk()
                    print(f"Downloading file {img.get('name')} from google drive [{int(status.progress() * 100):2d}%]", flush=True)


                if not os.path.exists(path):
                    os.makedirs(path)
                    print(f" {path} created", flush=True)

                with open(os.path.join(path,img.get('name')), "wb") as f:
                    f.write(file_header.getbuffer())

class OtherDriveProvider(Storage):

    def __init__(self):
        pass

    def upload():
        print("todo")
