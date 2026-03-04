import requests
import json
import os
from dotenv import load_dotenv
from datetime import date



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
    
def batch_list(video_id_lst, batch_size=50):
    for i in range(0, len(video_id_lst), batch_size):
        yield video_id_lst[i:i + batch_size]



def extract_video_details(video_id_lst):

    video_details = []
    for batch in batch_list(video_id_lst):
        ids = ",".join(batch)
        url = f"https://youtube.googleapis.com/youtube/v3/videos?part=contentDetails&part=snippet&part=statistics&id={ids}&key={API_KEY}"
        try:
            response = requests.get(url)
            response.raise_for_status()  # Check if the request was successful
            data = response.json()
            for item in data["items"]:
                video_details.append({
                    "videoId": item["id"],
                    "title": item["snippet"]["title"],
                    "publishedAt": item["snippet"]["publishedAt"],
                    "duration": item["contentDetails"]["duration"],
                    "viewCount": item["statistics"].get("viewCount", 0),
                    "likeCount": item["statistics"].get("likeCount", 0),
                    "commentCount": item["statistics"].get("commentCount", 0)
                })
            video_details.extend(data["items"])
        except requests.exceptions.RequestException as e:
            raise e
    print(f"Total Video Details Retrieved: {len(video_details)}")
    return video_details


def save_to_json(data, filename="video_details.json"):
    file_path = f'./data/YT_data_{date.today()}.json'
    with open(file_path, 'w',encoding='utf-8') as f:
        json.dump(data, f, indent=4,ensure_ascii=False)



if __name__ == "__main__":
    playlist_Id=get_playlist_id()
    video_id=get_video_ids(playlist_Id)
    video_data=extract_video_details(video_id)
    save_to_json(video_data)