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

startTime = time.time()
CHAT_MSG = re.compile(r"^:\w+!\w+@\w+\.tmi\.twitch\.tv PRIVMSG #\w+ :")

# some new stuff
webbrowser.open_new_tab("https://accounts.spotify.com/authorize?client_id=b43814b37f824be2a42a3ec2345d00b7&response_type=code&redirect_uri=https://val-kyr.com/bot_auth/callback/&scope=user-read-private%20user-read-email%20user-read-currently-playing&state=34fFs29kd09&show_dialog=True")
code = raw_input("What's the code?: ")

headers = {
	'Accept': 'application/json',
}
data = {
	'client_id': 'b43814b37f824be2a42a3ec2345d00b7',
	'client_secret': 'a334f80a1f3b42cb8415f6066d8297fd',
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


headers = {
    'Accept': 'application/json',
    'Content-Type': 'application/json',
    'Authorization': token_type + ' ' + access_token,
}
params = (
    ('market', 'ES'),
)
response = requests.get('https://api.spotify.com/v1/me/player/currently-playing', headers=headers, params=params)

y = json.loads(response.text)
print("<===========================================>")
print(str(y["item"]["artists"][0]["name"]) + " - " + y["item"]["name"])
# some new stuff

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

def GetSongSpotify():
	headers = {
	    'Accept': 'application/json',
	    'Content-Type': 'application/json',
	    'Authorization': token_type + ' ' + access_token,
	}
	params = (
	    ('market', 'ES'),
	)
	response = requests.get('https://api.spotify.com/v1/me/player/currently-playing', headers=headers, params=params)

	y = json.loads(response.text)
	return str(y["item"]["artists"][0]["name"]) + " - " + y["item"]["name"]

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
				utility.chat(s, "Song => " + GetSongSpotify())

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
