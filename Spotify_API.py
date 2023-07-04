import requests
import json
from datetime import date
from Refresh import Refresh
from Secrets import client_id_secret_b64_string as clientb64, access_token, userid, discover_weekly_id
import pandas as pd

class song:
    def __init__(self):
        self.token = access_token
        self.userid = userid
        self.discover_weekly_id = discover_weekly_id
        
    def user_liked_tracks(self):
        liked_songs = []
        
        query = 'https://api.spotify.com/v1/me/tracks?limit=50'
        header = {'Content-Type': 'application/json', 'Authorization': f"Bearer {self.token}"}
        
        response = requests.get(query,  headers = header)
        response_json = response.json()
        #print(response_json)
        
        
        while response_json['next'] != None:
                   
            for i in response_json['items']:
                artists = []
                for j in i['track']['artists']:
                    artists.append(j['name'])
                    
                liked_songs.append((i['added_at'], i['track']['name'],artists, i['track']['uri'].split(':')[-1]))
            
            response = requests.get(response_json['next'],  headers = header)
            response_json = response.json()
        
        for i in response_json['items']:
            artists = []
            for j in i['track']['artists']:
                artists.append(j['name'])
            liked_songs.append((i['added_at'], i['track']['name'],artists, i['track']['uri'].split(':')[-1]))
            
        liked_songs_df = pd.DataFrame(liked_songs, columns = ('added_at', 'name','artists','spotify_uri'))
        liked_songs_dict = liked_songs_df.to_dict(orient = 'records')
        
        return liked_songs_dict
                
        
    def callRefresh(self):
        
        refreshCaller = Refresh()
        self.token = refreshCaller.refresh()
        



