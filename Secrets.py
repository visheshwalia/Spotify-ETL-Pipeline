import base64
#from Refresh import Refresh
import requests
import pandas as pd
client_id = ''
client_secret = ''
redirect_uri = ''
access_token = ''
refresh_token = ''
userid = 'visheshwaliaid'
discover_weekly_id = ''
username = 'postgres'
port = '5433'
password = ''
engine = 'InnoDB'
host = '127.0.0.1'
db = 'spotify_api'



client_id_secret = f"{client_id}:{client_secret}"
client_id_secret_str_bytes = client_id_secret.encode('ascii')
client_id_secret_b64_bytes = base64.b64encode(client_id_secret_str_bytes)
client_id_secret_b64_string = client_id_secret_b64_bytes.decode('ascii')


