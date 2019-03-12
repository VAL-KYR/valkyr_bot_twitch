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
import sys
reload(sys)
sys.setdefaultencoding('utf8')

# ini tools
import ConfigParser
Config = ConfigParser.ConfigParser()
def ConfigSectionMap(section): # ini helper function
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

class Token(object): # Token Objects
    def __init__(self, Name, Text, Type, Scope, ExpireTime):
        self.name = Name # string
        self.text = Text # string
        self.type = Type # string
        self.scope = Scope # string
        self.expiry = ExpireTime # int
        self.timeUntilExpiry = self.expiry # int

    #++ make read/write to file extensions later for more complex file reading
    def decay(self): # coundown to token death
        time.sleep(1)
        self.timeUntilExpiry = str(int(self.timeUntilExpiry) - 1)
        return self.timeUntilExpiry
CURR_TOKEN = None
ACCESS_TOKEN = None
REFRESH_TOKEN = None

def ConfigToToken(fileWithFullPath): # Reads a config file and RETURNS a Token
    Config.remove_section('token')
    Config.read(fileWithFullPath)
    Config.sections()

    print(Config.sections())
    return Token(ConfigSectionMap("token")['name'], ConfigSectionMap("token")['text'], ConfigSectionMap("token")['type'], ConfigSectionMap("token")['scope'], ConfigSectionMap("token")['expiry'])
def TokenToConfig(fileWithFullPath, token): # Writes and/or Creates a config file with Token info
    Config.remove_section('token')
    cfgfile = open(fileWithFullPath, 'w')

    Config.add_section('token')
    Config.set('token','name', token.name)
    Config.set('token','text', token.text)
    Config.set('token','type', token.type)
    Config.set('token','scope', token.scope)
    Config.set('token','expiry', token.expiry)

    print(Config.sections())
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

    # this info also exists if needed y['access_token']
    refresh_token = Token('refresh_token', y["refresh_token"], y["token_type"], y["scope"], y["expires_in"])
    return refresh_token # Returns a auth_access_token with a .refresh token's text
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


    access_token = Token('access_token', y["access_token"], y["token_type"], y["scope"], y["expires_in"])
    return access_token #Returns an access token WITH it's type tag

### SPOTIFY OPERATIONS ###
def GetCurrSong(token):
    print('== GETTING CURRENT TRACK ==')
    print('With token => ' + str(token))

    #++ token_string = token_type + ' ' + access_token
    headers = {
        'Accept': 'application/json',
        'Content-Type': 'application/json',
        'Authorization': token.type + ' ' + token.text,
    }
    params = (
        ('market', 'ES'),
    )
    response = requests.get('https://api.spotify.com/v1/me/player/currently-playing', headers=headers, params=params)
    #print(response.text)
    try:
        y = json.loads(response.text)
        message = "<3 " + str(y["item"]["artists"][0]["name"]) + " - " + y["item"]["name"]
        message += " || " + y["item"]["external_urls"]["spotify"]
    except Exception as e:
        print(response.text)
        print(e)
        message = 'No song currently playing'



    return message.decode('utf-8') #Returns a song name using a passed token

### APPLICATION START OPERATIONS ###
def Init(): # GETS TOKENS FROM FILE OR ASKS TO RE-AUTH
    global CURR_TOKEN
    global ACCESS_TOKEN
    global REFRESH_TOKEN
    print('')
    print('=== REAL SPOTIFY INIT START ===')

    if os.path.isfile('./access_token.ini'):
        print('')
        print('== USING TOKEN FILE ==')
        with open('access_token.ini', 'r+') as tokenFile:
            if os.stat('./refresh_token.ini').st_size == 0:
                print('')
                print('== FILLING A TOKEN FILE ==')
                webbrowser.open_new_tab("https://accounts.spotify.com/authorize?client_id=b43814b37f824be2a42a3ec2345d00b7&response_type=code&redirect_uri=https://val-kyr.com/bot_auth/callback/&scope=user-read-private%20user-read-email%20user-read-currently-playing&state=34fFs29kd09&show_dialog=True")
                authCode = raw_input("What's the code?: ")
                #++ if complaint about missing type
                #++ token_string = token_type + ' ' + access_token
                REFRESH_TOKEN = GetToken(authCode)
                ACCESS_TOKEN = RefreshToken(REFRESH_TOKEN.text)
                TokenToConfig('./refresh_token.ini', REFRESH_TOKEN)
                TokenToConfig('./access_token.ini', ACCESS_TOKEN)
            else:
                print('')
                print('== READING TOKEN FILE ==')
                #++ refresh before access on read
                REFRESH_TOKEN = ConfigToToken('./refresh_token.ini')
                ACCESS_TOKEN = ConfigToToken('./access_token.ini')
    else:
        print('')
        print('== GENERATING A TOKEN FILE ==')
        with open('access_token.ini', 'w') as tokenFile:
            webbrowser.open_new_tab("https://accounts.spotify.com/authorize?client_id=b43814b37f824be2a42a3ec2345d00b7&response_type=code&redirect_uri=https://val-kyr.com/bot_auth/callback/&scope=user-read-private%20user-read-email%20user-read-currently-playing&state=34fFs29kd09&show_dialog=True")
            authCode = raw_input("What's the code?: ")
            #++ if complaint about missing type
            #++ token_string = token_type + ' ' + access_token
            REFRESH_TOKEN = GetToken(authCode)
            ACCESS_TOKEN = RefreshToken(REFRESH_TOKEN.text)
            TokenToConfig('./refresh_token.ini', REFRESH_TOKEN)
            TokenToConfig('./access_token.ini', ACCESS_TOKEN)

    print('=== REAL SPOTIFY INIT FINISHED ===')
    print('')


    CURR_TOKEN = ACCESS_TOKEN
    print('')
    print('== REFRESH_TOKEN == ')
    print(REFRESH_TOKEN)
    print('== ACCESS_TOKEN == ')
    print(ACCESS_TOKEN)
    print('== CURR_TOKEN == ')
    print(CURR_TOKEN)

    # do a test of the CURR_TOKEN
    print('')
    print(GetCurrSong(CURR_TOKEN))

### APPLICATION ONGOING OPERATIONS ###
def Update():
    global CURR_TOKEN
    global ACCESS_TOKEN
    global REFRESH_TOKEN

    while True:
        if CURR_TOKEN is not None:
            print(CURR_TOKEN.decay())
            if int(CURR_TOKEN.timeUntilExpiry) < 60:
                ACCESS_TOKEN = RefreshToken(REFRESH_TOKEN.text)
                TokenToConfig('./access_token.ini', ACCESS_TOKEN)
                CURR_TOKEN = ACCESS_TOKEN
                print(str(CURR_TOKEN) + ' with expiry of ' + str(CURR_TOKEN.expiry) + ' was renewed!')
