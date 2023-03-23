import os
import time
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from itertools import islice

# Target url [pexels #funnyanimals]
url = 'https://www.pexels.com/search/videos/living%20room/?orientation=landscape'

# Declare empty variable for all videos links
video_links = []

# try to get all video links
def get_video_links():
    options = webdriver.ChromeOptions()
    options.add_argument('--lang=en')
    options.add_experimental_option("excludeSwitches", ["enable-logging"])
    options.add_experimental_option("detach", True)
    browser = webdriver.Chrome(options=options, service=ChromeService(ChromeDriverManager().install()))
    browser.maximize_window()
    time.sleep(2)
    browser.get(url)
    time.sleep(5)
    '''
    Waiting for page of all content to show up
    '''
    for i in range(20):
        try:
            browser.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(5)
        except Exception as e:
            print(e, 'could not press search for new content')


    videos = input("How many videos you want to download? ")
    soup = BeautifulSoup(browser.page_source, 'lxml')
    links = soup.findAll('source')
    for link in islice(links, int(videos)):
        video_links.append(link.get('src'))
        if len(video_links) > 200:
            break
    
    return video_links

# download all videos
def download_video_series(video_links):
 
    for link in video_links:
        fn = link.split('/')[-1]  
        file_name = fn.split("?")[0]
        print ("Downloading video: %s"%file_name)
        # create response object
        r = requests.get(link, stream= True)
        try:
            video_dir = './videos/scrap_videos/'
            if not os.path.exists(video_dir):
                os.makedirs(video_dir)
            with open(video_dir+file_name, 'wb') as f:
                for chunk in r.iter_content(chunk_size= 1024*1024):
                    if chunk:
                        f.write(chunk)
            print("%s downloaded!"%file_name)
        except Exception as e:
            print(e, 'unable to get video')

if __name__ == '__main__':
    # getting all video links
    video_links = get_video_links()
    # download all videos
    download_video_series(video_links)