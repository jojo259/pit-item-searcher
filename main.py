import requests
import time

import pymongo
from pymongo import InsertOne, DeleteMany, ReplaceOne, UpdateOne
client = pymongo.MongoClient("mongodb://localhost:27017/")
db = client["pitdb"]
itemscol = db["items"]
playerscol = db["players"]

def doRequest(url):
	try:
		apiCalled = requests.get(url,timeout=3).json()
		return apiCalled
	except:
		print('api timeout probably')
		return {'success':False,'cause':'incode'}

def checkPlayer(playerUsername):
	toCheckUrl = f'https://api.hypixel.net/player?key={apiKey}&name={playerUsername}'

pageAt = 0
while pageAt < 4000:
	try:
		print(f'page {pageAt}')
		lbPlayers = doRequest(f'https://pitpanda.rocks/api/leaderboard/xp?page={pageAt}')
		if lbPlayers['success']:
			pageAt += 1
			if len(lbPlayers['leaderboard']) > 0:
				for lbPlayer in lbPlayers['leaderboard']:
					playerUuid = lbPlayer['uuid']
					playerUsername = lbPlayer['name']
					if ']' in playerUsername:
						playerUsername = playerUsername.split(']')[1][3:]
					else: #no rank
						playerUsername = playerUsername[5:]
					checkPlayer(playerUsername)
			else:
				pass
		else:
			pass
	except:
		pass

print('done')