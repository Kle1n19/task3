from requests import post,get
import base64
client_id = 'a00322244a5444d6942eb13431ef31fa'
client_secret = '78dd9f8792ee4ba7893f9748e84d2c5c'

def get_token():
    auth_url = 'https://accounts.spotify.com/api/token'
    client_creds = f"{client_id}:{client_secret}"
    client_creds_b64 = base64.b64encode(client_creds.encode())
    grant_type = 'client_credentials'
    body_params = {'grant_type': grant_type}
    auth_headers = {'Authorization': f'Basic {client_creds_b64.decode()}'}
    response = post(auth_url, data=body_params, headers=auth_headers)
    access_token = response.json()['access_token']
    return access_token

token = get_token()

def get_auth_header(token):
    return {'Authorization': 'Bearer '+ token}

def get_top_song(artist_name):
    query = f'artist:{artist_name}'
    response = get(f'https://api.spotify.com/v1/search?q={query}&type=track&limit=1', headers=get_auth_header(token))
    search_results = response.json()
    if search_results['tracks']['total'] == 0:
        return None
    else:
        return search_results['tracks']['items'][0]['name']