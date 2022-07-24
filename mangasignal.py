#!/usr/bin/python3

import os
import praw
import phue
import pprint
import time

from phue import Bridge
from datetime import datetime
from dateutil.parser import parse
from suntime import Sun, SunTimeException

#Coordinates of our location
latitude = 51.316811
longitude = -0.559080

sun = Sun(latitude, longitude)

today_sunset = sun.get_sunset_time()

onepiece_value = {'hue' : 1000, 'saturation': 254, 'transitiontime' : 30}
bokunohero_value = {'hue' : 30000, 'saturation': 254, 'transitiontime' : 30}
onepunch_value = {'hue' : 47500, 'saturation': 254, 'transitiontime' : 30}
spyxfamily_value = {'hue' : 57000, 'saturation': 254, 'transitiontime' : 30}


lights = []

def redditConnect():
#Client ID, secret, and user agent values that are be passed into the API. The credentials are stored as environment variables on my own device.
    connection = praw.Reddit(
        client_id = os.environ.get('REDDIT_CLIENT_ID'),
        client_secret = os.environ.get('REDDIT_CLIENT_SECRET'),
        user_agent = 'ChapterChecker by u/bowlama')

    return connection

def setLamp(lights, series):
    
    lights[3].transitiontime = series['transitiontime']
    lights[3].on = True
    lights[3].hue = series['hue']
    lights[3].saturation = series['saturation']
    lights[3].brightness = 80

def bridgeConnect(): 
    try:

        bridge_ip_addr = os.environ.get('BRIDGE_IP_ADDRESS')
        bridge = Bridge(bridge_ip_addr)

        bridge.connect()
    except:
        print('Unable to connect to Bridge. Please double-check your connectivity to the Hue Bridge')
    
    light_names = bridge.get_light_objects('id')
    return light_names

def getCurrentTime():

    current_time=time.localtime()        
    current_time_hour = int(current_time.tm_hour)
    current_time_min = int(current_time.tm_min)
    return current_time_min, current_time_hour

def getLatestOnePiece(reddit):
    for submission in reddit.subreddit("OnePiece").hot(limit=5):
        if submission.link_flair_text == 'Current Chapter':
            #If the post was submitted in the last 24 hours. This is 24 hours in seconds
            if (time.time() - submission.created_utc) < 86400:
                setLamp(lights, onepiece_value)

def getLatestBokuNoHero(reddit):
    for submission in reddit.subreddit("BokuNoHeroAcademia").hot(limit=5):
        if 'official release' in submission.title.lower():
            if (time.time() - submission.created_utc) < 86400:
                setLamp(lights, bokunohero_value)

def getLatestOnePunch(reddit):
    for submission in reddit.subreddit("OnePunchMan").hot(limit=5):
        if submission.link_flair_text == 'Murata Chapter':
            if (time.time() - submission.created_utc) < 86400:
                setLamp(lights, onepunch_value)

def getLatestSpyXFamily(reddit):
    for submission in reddit.subreddit("SpyXFamily").hot(limit=2):
        if 'disc' and 'chapter' in submission.title.lower():
            if (time.time() - submission.created_utc) < 86400:
                setLamp(lights, spyxfamily_value)
    



def main():
    global lights

    reddit = redditConnect()
    lights = bridgeConnect()
    sunset_loop = True
    max_time = 600

    while sunset_loop == True:

        if parse(str(datetime.utcnow())).timestamp() >= parse(str(today_sunset)).timestamp():
            sunset_loop = False
        else:
            current_time_min, current_time_hour = getCurrentTime() 
            if current_time_min == 0 or current_time_min % 20 == 0:
                start = time.time()
                ten_min_loop = True
                while ten_min_loop == True:
                    time.sleep(2)
                    getLatestOnePiece(reddit)
                    time.sleep(2)
                    getLatestBokuNoHero(reddit)
                    time.sleep(2)
                    getLatestOnePunch(reddit)
                    time.sleep(2)
                    getLatestSpyXFamily(reddit)
                    time.sleep(2)
                    #Stop the loop after 10 minutes
                    if time.time() - start >= max_time:
                        print('Stopping')
                        lights[3].on = False
                        ten_min_loop = False

                    else:
                        continue
            else:
                continue

if __name__ == "__main__":
    main()