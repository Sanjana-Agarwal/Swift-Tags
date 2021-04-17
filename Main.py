from tkinter import messagebox
from tkinter import *
from tkinter import simpledialog
import tkinter
import numpy as np
from tkinter import simpledialog
from tkinter import filedialog
import os
import re
from youtube_api import YouTubeDataAPI
import requests
import datetime
import json
import tweepy
from selenium import webdriver
import time, urllib.request, requests, os
from selenium import webdriver
import time, urllib.request, requests, os


main = tkinter.Tk()
main.title("SWIFT TAGS")  # designing main screen
main.geometry("1300x1200")

global tags_db
api_key = 'AIzaSyDSVujRgsnGt9xyeN0uzU9tlxYgf3tVgmw'
yt = YouTubeDataAPI(api_key)
global data


def upload():
    global tags_db
    filename = filedialog.askopenfilename(initialdir="dataset")
    tags_db = np.load(filename)
    text.delete('1.0', END)
    text.insert(END, filename + " loaded\n")
    text.insert(END, 'Total tags found in database : ' + str(len(tags_db)))


def youtube():
    text.delete('1.0', END)
    global data
    data = []
    input_data = tf1.get()
    input_data = input_data.strip().lower()
    tags = yt.search(q=input_data, maxResults=10, order_by='relevance', published_after=datetime.datetime(2013, 1, 1),
                     published_before=datetime.datetime(3000, 1, 1))
    videos = []
    response = requests.get(
        'https://www.googleapis.com/youtube/v3/search?q=' + input_data + '&key=AIzaSyDSVujRgsnGt9xyeN0uzU9tlxYgf3tVgmw&maxResults=10&chart=mostPopular&regionCode=US')
    response_json = json.loads(response.text)
    if response_json.get('items'):
        for item in response_json.get('items'):
            for k, v in item.items():
                if type(v) is dict:
                    for a, b in v.items():
                        if a == 'videoId':
                            videos.append(str(b))
    for i in range(len(videos)):
        print(videos[i])
        md = yt.get_video_metadata(videos[i])
        tag = md['video_tags']
        temp = tag.replace("|", ",")
        arr = temp.split(",")
        count = 0
        for i in range(len(arr)):
            if arr[i] not in data and count < 20:
                data.append(arr[i].strip().lower())
                count = count + 1
    text.insert(END, 'Top 20 Youtube Tags Suggestions\n\n')
    count = 0
    for i in range(len(data)):
        text.insert(END, "Suggested Tag Name : #" + data[i] + "\n")
        count = count + 1
        if count >= 20:
            break


def isEnglish(text):
    try:
        text.encode(encoding='utf-8').decode('ascii')
    except UnicodeDecodeError:
        return False
    else:
        return True


def get_woeid(api, locations):
    twitter_world = api.trends_available()
    places = {loc['name'].lower(): loc['woeid'] for loc in twitter_world};
    woeids = []
    for location in locations:
        if location in places:
            woeids.append(places[location])
        else:
            print("err: ", location, " woeid does not exist in trending topics")
    return woeids


def get_trending_hashtags(api, location):
    woeids = get_woeid(api, location)
    trending = set()
    for woeid in woeids:
        try:
            trends = api.trends_place(woeid)
        except:
            print("API limit exceeded. Waiting for next hour")
            # time.sleep(3605) # change to 5 for testing
            trends = api.trends_place(woeid)
        # Checking for English dialect Hashtags and storing text without #
        topics = [trend['name'][1:] for trend in trends[0]['trends'] if
                  (trend['name'].find('#') == 0 and isEnglish(trend['name']) == True)]
        trending.update(topics)

    return trending


def twitter():
    text.delete('1.0', END)
    auth = tweepy.OAuthHandler("aKBt8eJagd4PumKz8LGmZw", "asFAO5b3Amo8Turjl2RxiUVXyviK6PYe1X6sVVBA")
    auth.set_access_token("1914024835-dgZBlP6Tn2zHbmOVOPHIjSiTabp9bVAzRSsKaDX",
                          "zCgN7F4csr6f3eU5uhX6NZR12O5o6mHWgBALY9U4")
    api = tweepy.API(auth)
    data = get_trending_hashtags(api, ['india'])
    text.insert(END, 'Trending Twitter Tags\n\n')
    for tagname in data:
        text.insert(END, "Trending Tag Name : #" + tagname + "\n")


def instagram():
    driver = webdriver.Chrome()
    text.delete('1.0', END)
    input_data = tf1.get()
    input_data = input_data.strip().lower()
    input_data = input_data.replace(" ", "")
    max_id = None
    print(input_data)
    url = "https://www.instagram.com/explore/tags/" + input_data + "/"
    driver.get(url)
    posts = []
    links = driver.find_elements_by_tag_name('a')
    for link in links:
      post = link.get_attribute('href')
    if '/p/' in post:
      posts.append( post )
    print( posts )
    download_url = ''
    for post in posts:
      headers = {'User-Agent': 'Mozilla'}
      r = requests.get('{}?__a=1'.format( post ), headers=headers)
      data = r.json()['graphql']['shortcode_media']
      shortcode = data['shortcode']
    download_url = data['display_url']
    urllib.request.urlretrieve(download_url, 'Downloads/{}.jpg'.format(shortcode))
    print(download_url)  
    payload = {'__a': '1'}
    if max_id is not None:
        payload['max_id'] = max_id

    hashtags = []
    try:
        res = requests.get(url, params=payload).json()
        print(res)
        body = res["graphql"]['hashtag']
        cursor = res["graphql"]['hashtag']['edge_hashtag_to_media']['page_info']['end_cursor']
        for k, v in body.items():
            if k == 'edge_hashtag_to_top_posts':
                for a, b in v.items():
                    for i in range(len(b)):
                        for c, d in b[i].items():
                            for e, f in d.items():
                                if type(f) is dict:
                                    for g, h in f.items():
                                        if type(h) is list:
                                            for k in range(len(h)):
                                                for m, n in h[k].items():
                                                    for p, q in n.items():
                                                        arr = q.strip().split(" ")
                                                        for y in range(len(arr)):
                                                            arr[y] = arr[y].strip()
                                                            if arr[y].startswith('#'):
                                                                if arr[y] not in hashtags:
                                                                    hashtags.append(arr[y])
    except:
        raise
    text.insert(END, 'Top 20 Instagram Tags Suggestions\n\n')
    for i in range(0, 20):
        text.insert(END, "Suggested Tag Name : " + hashtags[i] + "\n")
    print("\n\n")
    print(hashtags)


def template():
    text.delete('1.0', END)
    text.insert(END, 'Youtube Description Templates\n\n')
    text.insert(END,
                'Hello Everyone, this is your ------channel name----- and I am again back with another video.\n Hope yo liked my video.\n And if you do then do not forget to Like Share and of course Subscribe my channel')


def quote():
    text.delete('1.0', END)
    text.insert(END, 'Instagram Quotation\n\n\n')
    text.insert(END, 'Love\n\n')
    text.insert(END, 'I swear I couldn’t love you more than I do right now, and yet I know I will tomorrow. \n')
    text.insert(END, 'I love you” begins by I, but it ends up by you.\n')
    text.insert(END, 'There is a madness in loving you, a lack of reason that makes it feel so flawless. \n')


font = ('times', 16, 'bold')
title = Label(main, text='SWIFT TAGS')
title.config(bg='LightGoldenrod1', fg='medium orchid')
title.config(font=font)
title.config(height=3, width=120)
title.place(x=0, y=5)

font1 = ('times', 12, 'bold')
text = Text(main, height=25, width=155)
scroll = Scrollbar(text)
text.configure(yscrollcommand=scroll.set)
text.place(x=10, y=200)
text.config(font=font1)

font1 = ('times', 12, 'bold')

l1 = Label(main, text='Your Input:')
l1.config(font=font1)
l1.place(x=50, y=100)

tf1 = Entry(main, width=80)
tf1.config(font=font1)
tf1.place(x=170, y=100)

uploadButton = Button(main, text="Load Tags Dataset", command=upload)
# uploadButton.place(x=50,y=150)
uploadButton.config(font=font1)

preButton = Button(main, text="Youtube Suggestion Tags", command=youtube)
preButton.place(x=210, y=150)
preButton.config(font=font1)

modelButton = Button(main, text="Twitter Suggestion Tags", command=twitter)
modelButton.place(x=420, y=150)
modelButton.config(font=font1)

classifierButton = Button(main, text="Instagram Suggestion Tags", command=instagram)
classifierButton.place(x=620, y=150)
classifierButton.config(font=font1)

templateButton = Button(main, text="Youtube Description Templates", command=template)
templateButton.place(x=840, y=150)
templateButton.config(font=font1)

quoteButton = Button(main, text="Instagram Quotation", command=quote)
quoteButton.place(x=1100, y=150)
quoteButton.config(font=font1)

main.config(bg='OliveDrab2')
main.mainloop()
