#!/usr/bin/env python

# python files
import config
import utility
import spotify
import ui

# tools
import socket
import time
import re
import random
import os
import base64
import threading
import sys
reload(sys)
sys.setdefaultencoding('utf8')

# Globals
connected = None
s = None
startTime = None
CHAT_MSG = None

# Threads
t_bot_init = None
t_bot_update = None
t_spot_init = None
t_spot_update = None
t_ui_display = None
t_close_event = None

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

def bot_init():
    global connected
    global s
    global startTime
    global CHAT_MSG

    # Twitch
    print('')
    print('== VAL_KYR TWITCH BOT INIT START ==')

    startTime = time.time()
    CHAT_MSG = re.compile(r"^:\w+!\w+@\w+\.tmi\.twitch\.tv PRIVMSG #\w+ :")

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

    print('connected ' + str(connected))
    print('s ' + str(s))
    print('startTime ' + str(startTime))
    print('CHAT_MSG ' + str(CHAT_MSG))

    print('== VAL_KYR TWITCH BOT INIT FINISHED ==')
    print('')
def bot_update(): # BOT RUNTIME CODE
    global connected
    global s
    global startTime
    global CHAT_MSG

    while connected:
        #++ MUTEX LOCKS TO BE REMOVED BY SERVICES
        # this will prevent running both services without a token or other spotify integrations
        # being ready to be used with !commands
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

            # response to helper words to give a list of command
            for pattern in config.PAT_HELP:
                if re.match(pattern, message):
                    utility.chat(s, ' SingsNote '.join(config.RES_CMDS))
                    break

            # timeout based on key words
            #++ establish a list of strikes, three !timeout strikes with that user and they're !banned
            for pattern in config.PAT_TIMEOUT:
                if re.match(pattern, message):
                    utility.timeout(s, username, 3600)
                    break

            # response to greetings
            for pattern in config.PAT_GREETING:
                if re.match(pattern, message):
                    utility.chat(s, random.choice(config.RES_GREETING) + " " + username)
                    break

            # !song cmd
            if re.match("!music", message):
                utility.chat(s, spotify.GetCurrSong(spotify.CURR_TOKEN))

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
def CloseEvent(): # Called when the ui window is closed
    while True:
        if ui.end == 0:
            print("Exiting...")
            os._exit(1)

if __name__ == "__main__":
    # Threads
    global t_bot_init
    global t_bot_update
    global t_spot_init
    global t_spot_update
    global t_ui_display
    global t_close_event

    t_bot_init = threading.Thread(target = bot_init)
    t_bot_update = threading.Thread(target = bot_update)
    t_spot_init = threading.Thread(target = spotify.Init)
    t_spot_update = threading.Thread(target = spotify.Update)
    t_ui_display = threading.Thread(target = ui.Display)
    t_close_event = threading.Thread(target = CloseEvent)

    # Init
    print('')
    print('@@@ PREPARING SERVICES @@@')
    print('')
    t_bot_init.start()
    t_bot_init.join()
    t_spot_init.start()
    t_spot_init.join()

    # Updates
    print('')
    print('@@@ RUNNING SERVICES @@@')
    print('')
    t_spot_update.start()
    #++ Have the bot update thread WAIT with MUTEX LOCKS on all services
    t_bot_update.start()
    t_ui_display.start()
    t_close_event.start()

    t_bot_update.join()
    t_spot_update.join()
    t_ui_display.join()
    t_close_event.join()
