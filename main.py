# -*- coding: UTF-8 -*-
#!/usr/bin/env python

# python files
import config
import utility
import spotify

# tools
import socket
import time
import re
import random
import json
import requests
import webbrowser
import os
import base64

startTime = time.time()
CHAT_MSG = re.compile(r"^:\w+!\w+@\w+\.tmi\.twitch\.tv PRIVMSG #\w+ :")

# Twitch
print('')
print('== STARTING VAL_KYR TWITCH BOT ==')

try: #Socket Attempts to Connect
    s = socket.socket()
    s.connect((config.HOST, config.PORT))
    s.send("PASS {}\r\n".format(config.PASS).encode("utf-8"))
    s.send("NICK {}\r\n".format(config.NICK).encode("utf-8"))
    s.send("JOIN {}\r\n".format(config.CHAN).encode("utf-8"))

    # Bot Greeting
    utility.chat(s, random.choice(config.RES_GREETING) + " chat!")
    connected = True #Socket succefully connected
except Exception as e:
    print(str(e))
    connected = False #Socket failed to connect

def FormattedTime(timeInSeconds):
    totalSeconds = timeInSeconds / 60.0
    totalMinutes = totalSeconds / 60.0
    totalHours = totalMinutes / 60.0
    totalDays = totalHours / 24.0

    seconds = timeInSeconds % 60.0
    minutes = totalSeconds % 60.0
    hours = totalMinutes % 60.0
    days = totalHours % 24.0

    officialTime = [int(seconds), int(minutes), int(hours), int(days)]
    niceTime = str(officialTime[0]) + " secs : " + str(officialTime[1]) + " mins : " + str(officialTime[2]) + " hrs : " + str(officialTime[3]) + " days "
    return niceTime #Returns a Nice Time

def GetSongSpotify(token):
    print('== GETTING CURRENT TRACK ==')
    print('With token => ' + token)

    headers = {
        'Accept': 'application/json',
        'Content-Type': 'application/json',
        'Authorization': token,
    }
    params = (
        ('market', 'ES'),
    )
    response = requests.get('https://api.spotify.com/v1/me/player/currently-playing', headers=headers, params=params)
    #print(response.text)
    y = json.loads(response.text)
    try:
        message = "<3 " + str(y["item"]["artists"][0]["name"]) + " - " + y["item"]["name"]
        message += " || " + y["item"]["external_urls"]["spotify"]
    except Exception as e:
        print(response.text)
        print(e)

    return message.decode('utf-8') #Returns a song name using a passed token

### SPOTIFY START OPERATIONS ###
spotify.Init()

def bot_loop(): # BOT RUNTIME CODE
    while connected:
        ### SPOTIFY ONGOING OPERATIONS ###
        spotify.Update()

        response = s.recv(1024).decode("utf-8")

        if response == "PING :tmi.twitch.tv\r\n":
            s.send("PONG :tmi.twitch.tv\r\n".encode("utf-8"))
            print("Sent Pong for server's Ping")
            print("Bot Uptime " + FormattedTime(time.time() - startTime))
            utility.chat(s, "Bot Uptime " + FormattedTime(time.time() - startTime))

        else:
            username = re.search(r"\w+", response).group(0)
            message = CHAT_MSG.sub("", response)
            print(username + ": " + response)

            # ban based on key words
            for pattern in config.PAT_BAN:
                if re.match(pattern, message):
                    utility.ban(s, username)
                    break

            # response to greetings
            for pattern in config.PAT_GREETING:
                if re.match(pattern, message):
                    utility.chat(s, random.choice(config.RES_GREETING) + " " + username)
                    break

            # !song cmd
            if re.match("!music", message):
                utility.chat(s, GetSongSpotify(token_full))

            # !quote cmd
            if re.match("!quote", message):
                utility.chat(s, random.choice(config.RES_QUOTE))

            # !uptime cmd
            if re.match("!uptime", message):
                utility.chat(s, "Bot Uptime " + FormattedTime(time.time() - startTime))

            # !wish cmd
            if re.match("!wish", message):
                utility.chat(s, random.choice(config.RES_WISHGRANTER) + " " + random.choice(config.RES_REACTORIMG))

        time.sleep(1 / config.RATE)

if __name__ == "__main__":
    bot_loop()
