import os
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.discovery import HttpError
from googleapiclient.http import MediaFileUpload
import pickle
import http.client
import httplib2
import random
import time

'''
pip install --upgrade google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client
'''

RETRIABLE_EXCEPTIONS = (httplib2.HttpLib2Error, IOError, http.client.NotConnected,
                        http.client.IncompleteRead, http.client.ImproperConnectionState,
                        http.client.CannotSendRequest, http.client.CannotSendHeader,
                        http.client.ResponseNotReady, http.client.BadStatusLine)
httplib2.RETRIES = 1
RETRIABLE_STATUS_CODES = [500, 502, 503, 504]
MAX_RETRIES = 10


# This method implements an exponential backoff strategy to resume a
# failed upload.

def resumable_upload(insert_request):
    response = None
    error = None
    retry = 0
    while response is None:
        try:
            print("Uploading file...")
            status, response = insert_request.next_chunk()
            if response is not None:
                if 'id' in response:
                    print("Video id '%s' was successfully uploaded." % response['id'])
                else:
                    exit("The upload failed with an unexpected response: %s" % response)
        except HttpError as e:
            if e.resp.status in RETRIABLE_STATUS_CODES:
                error = "A retriable HTTP error %d occurred:\n%s" % (e.resp.status,
                                                                     e.content)
            else:
                raise
        except RETRIABLE_EXCEPTIONS as e:
            error = "A retriable error occurred: %s" % e

        if error is not None:
            print(error)
            retry += 1
            if retry > MAX_RETRIES:
                exit("No longer attempting to retry.")

            max_sleep = 2 ** retry
            sleep_seconds = random.random() * max_sleep
            print("Sleeping %f seconds and then retrying..." % sleep_seconds)
            time.sleep(sleep_seconds)

    return response


def authenticate():
    credentials = None

    # checking if pickle file exists
    path_to_pickle = './token.pickle'
    if os.path.exists(path_to_pickle):
        print('loading credentials from file..')
        with open(path_to_pickle, 'rb') as token:
            credentials = pickle.load(token)

    # if not cred then make new ones
    if not credentials or not credentials.valid:
        if credentials and credentials.expired and credentials.refresh_token:
            print('refreshing access token...')
            credentials.refresh(Request())
        else:
            print('fetching new tokens...')
            flow = InstalledAppFlow.from_client_secrets_file(
                './client_secret.json',
                scopes=['https://www.googleapis.com/auth/youtube.upload']
            )
            flow.run_local_server(port=8080, prompt='consent', authorization_prompt_message='')

            credentials = flow.credentials

            with open(path_to_pickle, 'wb') as f:
                print('saving credentials for the future use...')
                pickle.dump(credentials, f)

    return credentials


def uploads_video_initialisation(video_to_upload, details):
    credentials = authenticate()
    # made this way, so you can doublecheck the details of the video
    description = details['desc']
    title = details['title']

    youtube = build('youtube', 'v3', credentials=credentials)
    request = youtube.videos().insert(
        part="snippet,status",
        body={
            "snippet": {
                "categoryId": "24",
                "description": description,
                "title": title
            },
            "status": {
                "privacyStatus": "private"
            }
        },

        # TODO: For this request to work, you must replace "YOUR_FILE"
        #       with a pointer to the actual file you are uploading.
        media_body=MediaFileUpload(video_to_upload, chunksize=-1, resumable=True)
    )
    # response = request.execute()
    response = resumable_upload(request)

    return response


def upload_thumbnail(image_path, video_id):
    credentials = authenticate()
    # print(response)

    youtube = build('youtube', 'v3', credentials=credentials)
    request = youtube.thumbnails().set(
        videoId=video_id,

        # TODO: For this request to work, you must replace "YOUR_FILE"
        #       with a pointer to the actual file you are uploading.
        media_body=MediaFileUpload(image_path)
    )

    response = request.execute()

    print(response)


def get_uploaded_videos():
    with open('./details/uploaded_videos.txt', mode='r') as file:
        return set((file.read()).split('\n'))

def save_uploaded_video(file_name):
    with open('./details/uploaded_videos.txt', mode='+a') as file:
        file.write(file_name+'\n')

if __name__ == '__main__':
    set_of_videos_uploaded = get_uploaded_videos()
    # path = './dance_videos/' 
    path = './videos/outputs/yt_video/'
    files = os.listdir(path)

    for file in files:
        if file in set_of_videos_uploaded:
            continue
        whole_path = path + file
        name = file.split('.')[0]
        details = {
            'desc': name.replace('_', ' ') + ' best of in 2022',
            'title' : name.replace('_', ' ')
        }
        details_on_video = uploads_video_initialisation(whole_path, details)
        id = details_on_video['id']
        thumbnail_path = f'./yt_thumbs/{name}.png'
        upload_thumbnail(thumbnail_path,video_id=id)
        save_uploaded_video(file_name=file)
        print('one video cycle completed')


# Lets try next
# https://github.com/viniciusenari/twitch-highlights-bot/blob/main/project/youtube.py

'''
import os
import random
import time
import httplib2

from project.video_content import VideoContent

import google_auth_oauthlib.flow
import googleapiclient.discovery
from googleapiclient.errors import HttpError

from googleapiclient.http import MediaFileUpload

scopes = ["https://www.googleapis.com/auth/youtube.upload"]
      

RETRIABLE_STATUS_CODES = [500, 502, 503, 504]
RETRIABLE_EXCEPTIONS = (httplib2.HttpLib2Error)
MAX_RETRIES = 10

class YoutubeUploader:

    def __init__(self):
        os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

        self.api_service_name = "youtube"
        self.api_version = "v3"
        self.client_secrets_file = "client_secret.json"

    def get_authenticated_service(self):
        flow = google_auth_oauthlib.flow.InstalledAppFlow.from_client_secrets_file(self.client_secrets_file, scopes)
        credentials = flow.run_console()
        self.youtube = googleapiclient.discovery.build(self.api_service_name, self.api_version, credentials=credentials)
    
    def upload_thumbnail(self, video_id, file_path):
        print('Uploading thumbnail...')
        request = self.youtube.thumbnails().set(
            videoId=video_id,
            media_body=file_path
        )
        response = request.execute()
        print(response)

    def upload_video(self, file_path, video_content):
        body = dict(
            snippet=dict(
                title=video_content.title,
                description=video_content.description,
                tags=video_content.tags,
                categoryId=video_content.category_id
            ),
            status=dict(
                privacyStatus=video_content.privacy_status
            )
        )

        insert_request = self.youtube.videos().insert(
            part=",".join(body.keys()),
            body=body,
            media_body= MediaFileUpload(
                file_path, chunksize=-1, resumable=True)
        )

        video_id = self.resumable_upload(insert_request)
        self.upload_thumbnail(video_id, 'files/youtube/thumbnail.png')

    def resumable_upload(self, insert_request):
        response = None
        error = None
        retry = 0
        while response is None:
            try:
                print("Uploading file...")
                status, response = insert_request.next_chunk()
                if response is not None:
                    if 'id' in response:
                        print("Video id '%s' was successfully uploaded." % response['id'])
                        return response['id']
                    else:
                        exit("The upload failed with an unexpected response: %s" % response)
            except HttpError as e:
                if e.resp.status in RETRIABLE_STATUS_CODES:
                    error = f"A retriable HTTP error {e.resp.status} occurred:\n{e.content}"
                else:
                    raise
            except RETRIABLE_EXCEPTIONS as e:
                error = f"A retriable error occurred: {e}"

            if error is not None:
                print(error)
                retry += 1
                if retry > MAX_RETRIES:
                    exit("No longer attempting to retry.")

                max_sleep = 2 ** retry
                sleep_seconds = random.random() * max_sleep
                print(f"Sleeping {sleep_seconds} seconds and then retrying...")
                time.sleep(sleep_seconds)
'''