import requests
import json
import os
from dotenv import load_dotenv


load_dotenv(dotenv_path="./.env")

API_KEY = os.getenv("API_KEY")
CHANNEL_HANDLE = "MrBeast"

def get_playlist_id():

    try:

        url = f"https://youtube.googleapis.com/youtube/v3/channels?part=contentDetails&forHandle={CHANNEL_HANDLE}&key={API_KEY}"

        response= requests.get(url)
        response.raise_for_status()  # Check if the request was successful
        data= response.json()
        Channel_items=data["items"][0]
        channel_playlistid = Channel_items["contentDetails"]['relatedPlaylists']['uploads']
        print(f"Channel Playlist ID: {channel_playlistid}")
        return channel_playlistid

    except requests.exceptions.RequestException as e:
        raise e
        

if __name__ == "__main__":
    get_playlist_id()