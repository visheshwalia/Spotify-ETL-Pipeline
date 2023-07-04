import base64
import json
import requests
from Secrets import refresh_token, client_id_secret_b64_string as clientb64

#print(refresh_token)

class Refresh():
    
    def __init__(self):
        self.clientb64 = clientb64
        self.refresh_token = refresh_token
        
    def refresh(self):
        
        query = 'https://accounts.spotify.com/api/token'
        
        data = {"grant_type": "refresh_token", "refresh_token" : refresh_token}
        
        header = {"Authorization": f"Basic {clientb64}"}
        #print(data)
        #print(header)
        #print(clientb64)
        response = requests.post(query, data = data, headers = header)
        #print(response)
         
        response_json = response.json()
        #print(response_json)
        
        return response_json['access_token']
    

    
#print(print(dir(x)))