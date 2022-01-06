import hypixel
import gzip
import zlib
import requests
import time
import nbt
import io
import base64
import random
import math
#from tinydb import TinyDB, Query
from nbt.nbt import NBTFile, TAG_Long, TAG_Int, TAG_String, TAG_List, TAG_Compound

try:
	apiKey = open('apiKey.txt').read()
except:
	print('create text file "apiKey"')

def checkItem(item):
	itemName = None
	try:
		itemName = item['tag']['display']['Name']
	except:
		pass
	if itemName != None:
		toOutput = False

		print(itemName)

		if toOutput:
			print()
			print(item)

def checkPlayer(playerUsername):
	#print(f'checking {playerUsername}')
	toCheckUrl = f'https://api.hypixel.net/player?key={apiKey}&name={playerUsername}'
	dataReceived = doRequest(toCheckUrl)
	if dataReceived != None:
		playerItems = getItems(dataReceived)
		for item in playerItems:
			checkItem(item)
	else:
		print('a')

def doRequest(url):
	returnedApi = False
	while not returnedApi:
		try:
			apiCalled = requests.get(url, timeout = 10).json()
			returnedApi = True
			return apiCalled
		except:
			print('api error, retrying')

def unpack_nbt(tag): #credit CrypticPlasma on hypixel forums
	"""
	Unpack an NBT tag into a native Python data structure.
	"""

	if isinstance(tag, TAG_List):
		return [unpack_nbt(i) for i in tag.tags]
	elif isinstance(tag, TAG_Compound):
		return dict((i.name, unpack_nbt(i)) for i in tag.tags)
	else:
		return tag.value

def decode_nbt(raw): #credit CrypticPlasma on hypixel forums, modified
	    """
	    Decode a gziped and base64 decoded string to an NBT object
	    """

	    return nbt.nbt.NBTFile(fileobj=io.BytesIO(raw))

def getItems(playerData):
	items = []
	toDecode = []

	try: #inventory
		toDecode.append(playerData['player']['stats']['Pit']['profile']['inv_contents']['data'])
	except:
		pass
	try: #enderchest
		toDecode.append(playerData['player']['stats']['Pit']['profile']['inv_enderchest']['data'])
	except:
		pass

	try: #stash
		toDecode.append(playerData['player']['stats']['Pit']['profile']['item_stash']['data'])
	except:
		pass

	try: #spire stash
		toDecode.append(playerData['player']['stats']['Pit']['profile']['spire_stash_inv']['data'])
	except:
		pass

	for curDecode in toDecode:
		temp = []
		for x in curDecode:
			if x < 0:
				temp.append(x + 256)
			else:
				temp.append(x)
		decoded = decode_nbt(bytes(temp))
		for tagl in decoded.tags:
			for tagd in tagl.tags:
				try:
					unpacked = unpack_nbt(tagd)
					if unpacked != {}:
						items.append(unpack_nbt(tagd))
				except:
					pass

	return items

print('starting')

pageAt = random.randint(1,3000)#int(input('What page of XP leaderboards to start at?\n'))
while pageAt < 9999:
	#try:
	print(f'page {pageAt}')
	lbPlayers = doRequest(f'https://pitpanda.rocks/api/leaderboard/xp?page={pageAt}')
	if lbPlayers['success']:
		print(f'got lb page {pageAt}')
		pageAt += 1
		if len(lbPlayers['leaderboard']) > 0:
			for lbPlayer in lbPlayers['leaderboard']:
				playerUuid = lbPlayer['uuid']
				playerUsername = lbPlayer['name']
				if ']' in playerUsername:
					playerUsername = playerUsername.split(']')[1][3:]
				else: #no rank
					playerUsername = playerUsername[5:]
				#print(f'checking {playerUsername}')
				checkPlayer(playerUsername)
		else:
			break
	else:
		pass
	#except:
	#	print('mainloop error')

print('done')