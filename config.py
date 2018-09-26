HOST = "irc.twitch.tv"							# Twitch IRC channel
PORT = 6667										# IRC port
NICK = "valkyr_bot"								# bot username
PASS = "oauth:l2cfmt5u5k2zltv9kf780g2tmjut2f" 	# OAUTH
CHAN = "#valkyr_dev"							# channel to join
RATE = 20.0 / 30.0									# messages per second
SMG_LOC = "E:\_RUN_ZIP\SMG\current_song.txt"	# location of current song folder from SMG
PAT_BAN = [										# the strings that trigger user ban
	r"gymbag",
	r"ourdaddytaughtusnottobeashamedofourdicks"
]
PAT_GREETING = [								# the strings that trigger greeting responses
	r"hello",
	r"hi",
	r"hiya"
]
RES_GREETING = [								# the reponse strings to greetings
	r"Hello",
	r"Hi",
	r"Hiya",
	r"Howdy"
]
PAT_QUOTE = [									# dev quotes
	r'"(◡‿◡✿)" - Val 2018',
	r'"every day is stumbling closer to bliss through the haze of failure and happy accidents" - Val 2018',
	r'"my life is the kitchen table" - Val 2018',
	r'"If I ever start a band I\'m calling it pseudovaries" - Val 2018',
	r'"I feel uncomfortable with beating something until it becomes delicious" - Val 2018'
]
