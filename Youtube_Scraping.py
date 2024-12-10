import os
import pandas as pd
from googleapiclient.discovery import build

# Replace with your own API key
API_KEY = 'AIzaSyBjXE5VzV0IOlUiBi4kCpAzyTlCZXQPLD8'
CHANNEL_ID = 'UCEeEQxm6qc_qaTE7qTV5aLQ'

# Build the YouTube API client
youtube = build('youtube', 'v3', developerKey=API_KEY)

# Function to get channel statistics
def get_channel_stats(youtube, channel_id):
    try:
        request = youtube.channels().list(
            part='snippet,contentDetails,statistics',
            id=channel_id
        )
        response = request.execute()
        return response
    except Exception as e:
        print(f"An error occurred while fetching channel stats: {e}")
        return None

# Function to get video statistics
def get_video_stats(youtube, channel_id):
    try:
        # Get the upload playlist ID
        request = youtube.channels().list(
            part='contentDetails',
            id=channel_id
        )
        response = request.execute()
        uploads_playlist_id = response['items'][0]['contentDetails']['relatedPlaylists']['uploads']
        print("Uploads Playlist ID:", uploads_playlist_id)  # Added for debugging

        # Get videos from the upload playlist
        videos = []
        request = youtube.playlistItems().list(
            part='snippet,contentDetails',
            playlistId=uploads_playlist_id,
            maxResults=50
        )
        response = request.execute()
        videos += response['items']
        print(f"Fetched {len(videos)} videos in the first request")  # Added for debugging

        while 'nextPageToken' in response:
            request = youtube.playlistItems().list(
                part='snippet,contentDetails',
                playlistId=uploads_playlist_id,
                maxResults=50,
                pageToken=response['nextPageToken']
            )
            response = request.execute()
            videos += response['items']
            print(f"Fetched {len(videos)} videos so far")  # Added for debugging

        print(f"Total videos fetched: {len(videos)}")  # Added for debugging

        # Get statistics for each video
        video_stats = []
        for video in videos:
            video_id = video['contentDetails']['videoId']
            request = youtube.videos().list(
                part='snippet,statistics,contentDetails',
                id=video_id
            )
            response = request.execute()
            if 'items' in response and len(response['items']) > 0:
                video_stats.append(response['items'][0])
                print(f"Fetched stats for video ID: {video_id}")  # Added for debugging
            else:
                print(f"No stats found for video ID: {video_id}")  # Added for debugging

        print(f"Total video stats fetched: {len(video_stats)}")  # Added for debugging
        return video_stats
    except Exception as e:
        print(f"An error occurred while fetching video stats: {e}")
        return None

# Fetch channel statistics
channel_stats = get_channel_stats(youtube, CHANNEL_ID)
if channel_stats:
    print("Channel Stats:", channel_stats)
    # Save the channel statistics to a CSV file
    channel_stats_df = pd.json_normalize(channel_stats['items'])
    channel_stats_df.to_csv('channel_stats.csv', index=False)
else:
    print("Failed to fetch channel statistics.")

# Fetch video statistics
video_stats = get_video_stats(youtube, CHANNEL_ID)
if video_stats:
    print("Video Stats:", video_stats)
    # Save the video statistics to a CSV file
    video_stats_df = pd.json_normalize(video_stats)
    video_stats_df.to_csv('video_stats.csv', index=False)
else:
    print("Failed to fetch video statistics.")
