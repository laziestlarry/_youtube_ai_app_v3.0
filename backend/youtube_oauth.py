import os
import pickle
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]

def get_authenticated_service():
    if os.path.exists("token.pickle"):
        with open("token.pickle", "rb") as token:
            return build("youtube", "v3", credentials=pickle.load(token))

    flow = InstalledAppFlow.from_client_secrets_file("client_secrets.json", SCOPES)
    creds = flow.run_local_server(port=8080)
    with open("token.pickle", "wb") as token:
        pickle.dump(creds, token)

    return build("youtube", "v3", credentials=creds)