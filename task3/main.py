from dotenv import load_dotenv
import base64
import json
from requests import post,get
from flask import Flask, redirect,url_for,request,render_template
import folium


load_dotenv()

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

def get_auth_header(token):
    return {'Authorization': 'Bearer '+ token}

def search_for_artist(token, artist_name):
    url = 'https://api.spotify.com/v1/search'
    headers = get_auth_header(token)
    query = f'?q={artist_name}&type=artist&limit=1'
    
    query_url = url + query
    result = get(query_url, headers=headers)
    json_result = json.loads(result.content)['artists']['items']
    if len(json_result) == 0:
        print('Artist not exist')
        return None
    return json_result[0]

def get_songs_by_artist(token,artist_id):
    url = f'https://api.spotify.com/v1/artists/{artist_id}/top-tracks?country=US'
    headers = get_auth_header(token)
    result = get(url,headers = headers)
    json_result = json.loads(result.content)['tracks']
    return json_result

token = get_token()
result = search_for_artist(token,'metallica')
artist_id = result['id']
songs = get_songs_by_artist(token,artist_id)

def get_track_markets(track_name):
    query = f'track:{track_name}'
    response = get(f'https://api.spotify.com/v1/search?q={query}&type=track&limit=1', headers=get_auth_header(token))
    search_results = response.json()
    if search_results['tracks']['total'] == 0:
        return None
    else:
        track_id = search_results['tracks']['items'][0]['id']
        response = get(f'https://api.spotify.com/v1/tracks/{track_id}', headers=get_auth_header(token))
        track_info = response.json()
        return track_info['available_markets']

def get_count_by_artist_name(name):
    result = search_for_artist(token,name)
    artist_id = result['id']
    songs = get_songs_by_artist(token,artist_id)

    countries = get_track_markets([song['name'] for song in songs][0])
    return countries
def get_coords(markets):
    coords = []
    names = []
    with open('/Users/petroprokopetz/Desktop/week2.2/task3/countries.csv','r',encoding = 'utf-8') as file:
        data = file.read().splitlines()
        for i ,line in enumerate(data):
            line = line.split(',')
            if line[0] in markets:
                coords.append((line[1],line[2]))
                names.append(line[3])
    return coords,names 
def gen_map(coords):
    map = folium.Map()
    fgg = folium.FeatureGroup(name="Countries")
    for row in coords[0]:
        fgg.add_child(folium.Marker(location=[row[0], row[1]],
                            popup=coords[1][coords[0].index(row)],
                            icon=folium.Icon()))
    map.add_child(fgg)
    map.save('new.html')
print(gen_map(get_coords(get_count_by_artist_name('metallica'))))