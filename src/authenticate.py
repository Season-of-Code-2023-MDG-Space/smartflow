import requests
from urllib.parse import unquote
import webbrowser
import json
from time import sleep
from dotenv.main import load_dotenv
import os

load_dotenv()

def authenticate_user():
    CLIENT_ID = os.environ['CLIENT_ID'] #SmartFlow oAuth app initialized

    # URL constants (for device flow) : https://docs.github.com/en/apps/oauth-apps/building-oauth-apps/authorizing-oauth-apps#device-flow
    AUTH_URL = "https://github.com/login/device/code"
    ACCESS_TOKEN_URL = "https://github.com/login/oauth/access_token"
    GRANT_TYPE = "urn:ietf:params:oauth:grant-type:device_code"

    # Verifying the user
    user_verification_data = {
        "client_id" : CLIENT_ID,
        "scope": "public_repo read:org",
    }

    x = requests.post(AUTH_URL, json = user_verification_data)
    response = dict([i.split('=') for i in x.text.split('&')])
    response['verification_uri'] = unquote(response['verification_uri'])

    print(f"Code for authentication: {response['user_code']}")
    sleep(1.5)

    with open(os.path.normpath('./src/auth_init.json'), 'w') as f:
        f.write(json.dumps(response, indent=4))

    webbrowser.open_new_tab(response['verification_uri'])

    # Checking if the user is successfully authenticated, and get the access token in a separate file.
    access_token_data = {
        "client_id" : CLIENT_ID,
        "device_code" : response['device_code'],
        "grant_type" : GRANT_TYPE
    }

    while True:
        x = requests.post(ACCESS_TOKEN_URL, json = access_token_data)
        
        if x.text.startswith('access_token'):
            response = dict([i.split('=') for i in x.text.split('&')])
            response['scope'] = unquote(response['scope'])
            
            with open(os.path.normpath('./src/access_token.json'), 'w') as file:
                file.write(json.dumps(response, indent=4))
            print(f"Authenticated successfully\u2705")
            break

        else:
            sleep(5) 
            # By default, the interval is 5s i.e.
            # The minimum number of seconds that must pass before you can make a new access token request.
            # If more than one request over 5s --> slow_down error.