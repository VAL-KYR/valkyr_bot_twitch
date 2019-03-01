# -*- coding: UTF-8 -*-

# python files
import config

# tools
import socket
import time
import re
import json
import requests
import webbrowser
import os
import base64

# ini tools
import ConfigParser

# ini helper function
def ConfigSectionMap(section):
    dict1 = {}
    options = Config.options(section)
    for option in options:
        try:
            dict1[option] = Config.get(section, option)
            if dict1[option] == -1:
                DebugPrint("skip: %s" % option)
        except:
            print("exception on %s!" % option)
            dict1[option] = None
    return dict1


# globals
# TOKENS
class Token(object):
    def __init__(Name, Text, Type, Scope, ExpireTime, Refresh = None):
        self.name = Name # string
        self.text = Text # string
        self.type = Type # string
        self.scope = Scope # string
        self.expiry = ExpireTime # int
        self.timeUntilExpiry = expiry # int
        self.refresh = Refresh # Token

    def decay(): # coundown to token death
        timeUntilExpiry -= 1
        time.sleep(1)

    #++ make read/write to file extensions later for more complex file reading

# config functions
def ConfigToToken(fileWithFullPath): # Reads a config file and RETURNS a Token
    Config = ConfigParser.ConfigParser()
    Config.read(fileWithFullPath)

    Config.sections()
    return Token(ConfigSectionMap("token")['name'], ConfigSectionMap("token")['text'], ConfigSectionMap("token")['type'], ConfigSectionMap("token")['scope'], ConfigSectionMap("token")['expiry'])
def TokenToConfig(fileWithFullPath, token): # Writes and/or Creates a config file with Token info
    Config = ConfigParser.ConfigParser()
    cfgfile = open(fileWithFullPath, 'w')

    Config.add_section('token')
    Config.set('token','name', token.name)
    Config.set('token','text', token.text)
    Config.set('token','type', token.type)
    Config.set('token','scope', token.scope)
    Config.set('token','expiry', token.expiry)
    if token.refresh is not None:
        Config.set('token','refresh', token.refresh)

    Config.write(cfgfile)
    cfgfile.close()
    return

def GetToken(code): # get first spotify token
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
    return token_string #Returns a refresh token WITHOUT it's type tag
def RefreshToken(token): # get real useable token
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
    return token_string #Returns an access token WITH it's type tag

### APPLICATION START OPERATIONS ###
def Init():
    print('@@@ REAL SPOTIFY INIT @@@')
    CURR_TOKEN = None
    ACCESS_TOKEN = None
    REFRESH_TOKEN = None

    if os.path.isfile('./access_token.ini'):
        print('')
        print('== USING TOKEN FILE ==')
        with open('access_token.ini', 'r+') as tokenFile:
            if os.stat('./access_token.ini').st_size == 0:
                print('')
                print('== FILLING A TOKEN FILE ==')
                webbrowser.open_new_tab("https://accounts.spotify.com/authorize?client_id=b43814b37f824be2a42a3ec2345d00b7&response_type=code&redirect_uri=https://val-kyr.com/bot_auth/callback/&scope=user-read-private%20user-read-email%20user-read-currently-playing&state=34fFs29kd09&show_dialog=True")
                authCode = raw_input("What's the code?: ")
                ACCESS_TOKEN = RefreshToken(GetToken(authCode))
                TokenToConfig('./access_token.ini', ACCESS_TOKEN)
            else:
                print('')
                print('== READING TOKEN FILE ==')
                ACCESS_TOKEN = ConfigToToken('./access_token.ini')
    else:
        print('')
        print('== GENERATING A TOKEN FILE ==')
        with open('access_token.ini', 'w') as tokenFile:
            webbrowser.open_new_tab("https://accounts.spotify.com/authorize?client_id=b43814b37f824be2a42a3ec2345d00b7&response_type=code&redirect_uri=https://val-kyr.com/bot_auth/callback/&scope=user-read-private%20user-read-email%20user-read-currently-playing&state=34fFs29kd09&show_dialog=True")
            authCode = raw_input("What's the code?: ")
            authCode = raw_input("What's the code?: ")
            ACCESS_TOKEN = RefreshToken(GetToken(authCode))
            TokenToConfig('./access_token.ini', ACCESS_TOKEN)


    CURR_TOKEN = ACCESS_TOKEN
    # do a test of the CURR_TOKEN

### APPLICATION ONGOING OPERATIONS ###
## decay the three tokens with the expire function
def Update():
    print('@@@ REAL SPOTIFY RUNTIME @@@')
    CURR_TOKEN.decay()
