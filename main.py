# -*- coding: UTF-8 -*-
#!/usr/bin/env python
import config
import utility
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

# auto-auth
'''
headers = {
    'Accept': 'application/json',
    'Content-Type': 'application/json',
    #'Authorization': token_type + ' ' + access_token,
}
params = (
    ('client_id', 'b43814b37f824be2a42a3ec2345d00b7'),
    ('response_type', 'code'),
    ('redirect_uri', 'https://val-kyr.com/bot_auth/callback/'),
    ('scope', 'user-read-private%20user-read-email%20user-read-currently-playing'),
    ('show_dialog', 'True'),
)
auth = requests.get("https://accounts.spotify.com/authorize", headers=headers, params=params)
y = json.loads(auth.text)
print(y)
'''
# auto-auth
# generates u.error u.server_error

# get first spotify token
def GetToken(code):
    print('')
    print('== FETCHING INITIAL TOKEN ==')

    headers = {
        'Authorization': 'Basic ' + base64.b64encode(config.CLIENT_ID + ":" + config.CLIENT_SECRET),
        'Accept': 'application/json',
    }
    data = {
        'grant_type': 'authorization_code',
        'code': code,
        'redirect_uri': 'https://val-kyr.com/bot_auth/callback/',
    }

    token = requests.post('https://accounts.spotify.com/api/token', headers=headers, data=data)
    y = json.loads(token.text)

    access_token = y["access_token"]
    token_type = y["token_type"]
    scope = y["scope"]
    expires_in = y["expires_in"]
    refresh_token = y["refresh_token"]

    print("<===========================================>")
    print("access_token " + access_token)
    print("token_type " + token_type)
    print("scope " + scope)
    print("expires_in " + str(expires_in))
    print("refresh_token " + refresh_token)

    token_string = refresh_token
    return token_string

def RefreshToken(token):
    print('')
    print('== REFRESHING TOKEN ==')

    headers = {
        'Authorization': 'Basic ' + base64.b64encode(config.CLIENT_ID + ":" + config.CLIENT_SECRET),
        'Accept': 'application/json',
    }
    data = {
        'grant_type': 'refresh_token',
        'refresh_token': token,
    }

    r_token = requests.post('https://accounts.spotify.com/api/token', headers=headers, data=data)
    y = json.loads(r_token.text)

    access_token = y["access_token"]
    token_type = y["token_type"]
    scope = y["scope"]
    expires_in = y["expires_in"]

    print("<===========================================>")
    print("access_token " + access_token)
    print("token_type " + token_type)
    print("scope " + scope)
    print("expires_in " + str(expires_in))

    token_string = token_type + ' ' + access_token
    return token_string

# Check for saved token
if os.path.isfile('./token.txt'):
    print('')
    print('== USING TOKEN FILE ==')
    with open('token.txt', 'r+') as tokenFile:
        if os.stat('./token.txt').st_size == 0:
            print('')
            print('== FILLING A TOKEN FILE ==')
            webbrowser.open_new_tab("https://accounts.spotify.com/authorize?client_id=b43814b37f824be2a42a3ec2345d00b7&response_type=code&redirect_uri=https://val-kyr.com/bot_auth/callback/&scope=user-read-private%20user-read-email%20user-read-currently-playing&state=34fFs29kd09&show_dialog=True")
            authCode = raw_input("What's the code?: ")
            token_full = RefreshToken(GetToken(authCode))
            tokenFile.write(token_full)
        else:
            print('')
            print('== READING TOKEN FILE ==')
            file_bits = tokenFile.read().split(' ')
            print('Contents => ' + str(file_bits[-1]))
            token_full = str(file_bits[-1])
else:
    print('')
    print('== GENERATING A TOKEN FILE ==')
    with open('token.txt', 'w') as tokenFile:
        webbrowser.open_new_tab("https://accounts.spotify.com/authorize?client_id=b43814b37f824be2a42a3ec2345d00b7&response_type=code&redirect_uri=https://val-kyr.com/bot_auth/callback/&scope=user-read-private%20user-read-email%20user-read-currently-playing&state=34fFs29kd09&show_dialog=True")
        authCode = raw_input("What's the code?: ")
        token_full = RefreshToken(GetToken(authCode))
        tokenFile.write(token_full)

# Twitch
print('')
print('== STARTING VAL_KYR TWITCH BOT ==')

try:
    s = socket.socket()
    s.connect((config.HOST, config.PORT))
    s.send("PASS {}\r\n".format(config.PASS).encode("utf-8"))
    s.send("NICK {}\r\n".format(config.NICK).encode("utf-8"))
    s.send("JOIN {}\r\n".format(config.CHAN).encode("utf-8"))
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
    return niceTime


def GetSong():
    with open(config.SMG_LOC, 'r') as smgSrc:
        songData = smgSrc.read()
        return songData

def GetSongSpotify(token):
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

    return message.decode('utf-8')

def bot_loop():
    while connected:
        response = s.recv(1024).decode("utf-8")

        if response == "PING :tmi.twitch.tv\r\n":
            s.send("PONG :tmi.twitch.tv\r\n".encode("utf-8"))
            print("Sent Pong for server's Ping")
            print("Bot Uptime " + FormattedTime(time.time() - startTime))

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
                utility.chat(s, FormattedTime(time.time() - startTime))

            # !wish cmd
            if re.match("!wish", message):
                utility.chat(s, random.choice(config.RES_WISHGRANTER) + " " + random.choice(config.RES_REACTORIMG))

        time.sleep(1 / config.RATE)

if __name__ == "__main__":
    bot_loop()
