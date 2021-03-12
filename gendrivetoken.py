from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

# NOTE If scopes are modified you need to delete the file token.json
SCOPES = ['https://www.googleapis.com/auth/drive.file']

def genTokenFromCreds(creds=None):
    # If there are no (valid) credentials available, let the user log in
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)

        # Save the credentials for the next run
        with open('token.json','w') as token:
            token.write(creds.to_json())
    return creds


if __name__ == "__main__":
    genTokenFromCreds()