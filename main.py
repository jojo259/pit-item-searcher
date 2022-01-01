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

apiKey = open('apiKey.txt').read()

def doRequest(url):
	try:
		apiCalled = requests.get(url, timeout = 10).json()
		return apiCalled
	except:
		#print('api timeout probably')
		return None

def checkItem(item):
	itemName = None
	try:
		itemName = item['tag']['display']['Name']
	except:
		pass
	if itemName != None:
		if 'Rage' in itemName:
			reg = 0
			ass = 0
			cf = 0
			mir = 0
			pero = 0
			for ench in item['tag']['ExtraAttributes']['CustomEnchants']:
				enchKey, enchLevel = ench['Key'], ench['Level']
				if enchKey == 'regularity':
					reg = enchLevel
				if enchKey == 'sneak_teleport':
					ass = enchLevel
				if enchKey == 'power_against_crits':
					cf = enchLevel
				if enchKey == 'immune_true_damage':
					mir = enchLevel
				if enchKey == 'regen_when_hit':
					pero = enchLevel

			good = False
			if reg > 0 and ass > 0:
				good = True

			if good:
				print()
				print(item)

			'''
			if reg == 3 and ass == 3:
				good = True
			if reg == 3 and cf == 3 and mir == 1:
				good = True
			if reg == 3 and pero == 3 and mir == 1:
				good = True
			if reg > 0 and ass >= 2 and cf == 3:
				good = True
			if reg > 0 and ass >= 2 and cf == 3:
				good = True
			if reg > 0 and ass >= 2 and cf == 3:
				good = True
			'''

def checkPlayer(playerUsername):
	toCheckUrl = f'https://api.hypixel.net/player?key={apiKey}&name={playerUsername}'
	dataReceived = doRequest(toCheckUrl)
	if dataReceived != None:
		playerItems = getItems(dataReceived)
		for item in playerItems:
			checkItem(item)
	else:
		print('a')

def decode_nbt(raw): #not mine
	data = nbt.nbt.NBTFile(fileobj=io.BytesIO(raw))
	return data

def unpack_nbt(tag): #not mine
	"""
	Unpack an NBT tag into a native Python data structure.
	"""

	if isinstance(tag, TAG_List):
		return [unpack_nbt(i) for i in tag.tags]
	elif isinstance(tag, TAG_Compound):
		return dict((i.name, unpack_nbt(i)) for i in tag.tags)
	else:
		return tag.value

def getItems(playerData):
	items = []
	toDecode = []

	try: #inv
		toDecode.append(playerData['player']['stats']['Pit']['profile']['inv_contents']['data'])
	except:
		pass
	try: #end
		toDecode.append(playerData['player']['stats']['Pit']['profile']['inv_enderchest']['data'])
	except:
		pass

	try: #sta
		toDecode.append(playerData['player']['stats']['Pit']['profile']['item_stash']['data'])
	except:
		pass

	try: #spr
		toDecode.append(playerData['player']['stats']['Pit']['profile']['spire_stash_inv']['data'])
	except:
		pass

	for curDecode in toDecode:
		newList = []
		for x in curDecode:
			if x < 0:
				newList.append(x + 256)
			else:
				newList.append(x)
		decoded = decode_nbt(bytes(newList))
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

pageAt = int(open('pageToStartAt.txt').read())
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
					#print(f'checking {playerUsername}')
					checkPlayer(playerUsername)
			else:
				pass
		else:
			pass
	except:
		pass

print('done')