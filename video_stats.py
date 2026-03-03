import requests
import json
import os
from dotenv import load_dotenv


load_dotenv(dotenv_path="./.env")

API_KEY = os.getenv("API_KEY")
CHANNEL_HANDLE = "MrBeast"
maxResults = 50

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
    


def get_video_ids(playlist_Id):

    
    video_ids = []
    pageToken = None

    base_url=f"https://youtube.googleapis.com/youtube/v3/playlistItems?part=contentDetails&maxResults={maxResults}&playlistId={playlist_Id}&key={API_KEY}"


    try:
        while True:
            url = f"{base_url}&pageToken={pageToken}" if pageToken else base_url
            response = requests.get(url)
            response.raise_for_status()  # Check if the request was successful
            data = response.json()

            for item in data["items"]:
                video_ids.append(item["contentDetails"]["videoId"])

            pageToken = data.get("nextPageToken")
            if not pageToken:
                break

        print(f"Total Video IDs Retrieved: {len(video_ids)}")
        return video_ids

    except requests.exceptions.RequestException as e:
        raise e

if __name__ == "__main__":
    playlist_Id=get_playlist_id()
    get_video_ids(playlist_Id)