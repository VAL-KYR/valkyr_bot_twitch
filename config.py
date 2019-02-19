# -*- coding: UTF-8 -*-
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
RES_QUOTE = [									# dev quotes
	r'"(◡‿◡✿)" - Val 2018',
	r'"uwu" - Val 2016',
	r'"every day is stumbling closer to bliss through the haze of failure and happy accidents" - Val 2018',
	r'"my life is the kitchen table" - Val 2018',
	r'"If I ever start a band I\'m calling it pseudovaries" - Val 2018',
	r'"I feel uncomfortable with beating something until it becomes delicious" - Val 2018'
]
RES_WISHGRANTER = [
	r'Пришло время. Я вижу твоё желание.',
	r'Твоя цель эдесь. Иди ко мне.',
	r'Путь завершен, человек. Иди ко мне.',
	r'Твое желание скоро исполнится. Иди ко мне.',
	r'Твой путь завершается. Иди ко мне.',
	r'Иди ко мне. Ты обретешь то, что заслуживаешь.'
	r'Вознаграждем будет только один.'
]
RES_REACTORIMG = [
	r'http://knowledgeglue.com/wp-content/uploads/2015/07/NZ82nkS.jpg',
	r'http://knowledgeglue.com/wp-content/uploads/2015/07/BeDdgGu.jpg',
	r'http://knowledgeglue.com/wp-content/uploads/2015/07/aCHCKvZ-735x1024.jpg',
	r'http://knowledgeglue.com/wp-content/uploads/2015/04/125-JV9nP4X-1024x612.jpg',
	r'http://knowledgeglue.com/wp-content/uploads/2015/04/126-1Ub3g6M-1024x666.jpg',
	r'http://knowledgeglue.com/wp-content/uploads/2015/04/124-RG9OOxn.jpg'
]
