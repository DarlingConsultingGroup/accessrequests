import requests
import json
import os


def get_access_token():
    url = "https://login.microsoftonline.com/9f6470ef-8763-434b-9e26-f88925eaabe9/oauth2/v2.0/token"
    payload = os.environ["dev_core_api_get_token_payload"]
    headers = {
        'Authorization': os.environ["dev_core_api_get_token_auth"],
        'Content-Type': 'application/x-www-form-urlencoded',
        'Cookie': os.environ["dev_core_api_cookie"]}
    response = requests.request("POST", url, headers=headers, data = payload)
    responseJSON = json.dumps(response.json())
    responseList = json.loads(responseJSON)
    return responseList["access_token"]