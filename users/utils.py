import os.path #Used to check if token.json exists

#Import all necessary imports for the Gmail API as indicated on the Google For Developer website
from google.auth.transport.requests import Request 
from google.oauth2.credentials import Credentials 
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

#Imports for creating and encoding the email message
from email.mime.text import MIMEText
import base64

#The scope of the Gmail API is limited to sending emails
SCOPES = ["https://www.googleapis.com/auth/gmail.send"]

def send_password_reset_email(user_email, reset_link):
    creds = None
    # Check if token.json exists, which stores the user's access and refresh tokens
    if os.path.exists("token.json"): #Checks if token.json exists 
        creds = Credentials.from_authorized_user_file("token.json", SCOPES) #If it exists, it loads credentials from the token file

    #Handling invalid or expired credentials
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token: #Check if credentials are expired
            creds.refresh(Request()) #Refresh the token if expired
        else: #If no valid credentials, start the OAuth2 authentication flow
            flow = InstalledAppFlow.from_client_secrets_file(
                "config/credentials.json", SCOPES
            )
            creds = flow.run_local_server(port=0)
        with open("token.json", "w") as token:
            token.write(creds.to_json()) #Save the new credentials to token.json for future use

    try:
        service = build("gmail", "v1", credentials=creds)
        
        # Create the email content using MIMEText
        message = MIMEText(f"Click the link to reset your password: {reset_link}") 
        message["to"] = user_email  
        message["subject"] = "Password Reset" 
        message["from"] = "your-email@gmail.com" #Set sender email (must be authenticated user)
        
        # Encode the email message in base64 as required by Gmail API
        raw = base64.urlsafe_b64encode(message.as_bytes()).decode()
        message_body = {"raw": raw}

        # Send the email using the Gmail API
        service.users().messages().send(userId="me", body=message_body).execute()

    #error handling
    except HttpError as error:
        print(f"An HTTP error occurred: {error}")
    except Exception as error:
        print(f"An error occurred: {error}")