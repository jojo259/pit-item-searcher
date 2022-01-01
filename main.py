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

def decode_nbt(raw):
	data = nbt.nbt.NBTFile(fileobj=io.BytesIO(raw))
	return data

def unpack_nbt(tag):
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

	try: #inv
		kvl = playerData['player']['stats']['Pit']['profile']['inv_contents']['data']
		newkvl = []
		for x in kvl:
			if x < 0:
				newkvl.append(x + 256)
			else:
				newkvl.append(x)
		inv=decode_nbt(bytes(newkvl))
		for tagl in inv.tags:
			for tagd in tagl.tags:
				try:
					items.append(tagd)
				except:
					''
	except:
		''
	try: #end
		kvl2 = playerData['player']['stats']['Pit']['profile']['inv_enderchest']['data']
		newkvl2 = []
		for x in kvl2:
			if x < 0:
				newkvl2.append(x + 256)
			else:
				newkvl2.append(x)
		inv2=decode_nbt(bytes(newkvl2))
		for tagl in inv2.tags:
			for tagd in tagl.tags:
				try:
					items.append(tagd)
				except:
					''
	except:
		''
	try: #sta
		kvl3 = playerData['player']['stats']['Pit']['profile']['item_stash']['data']
		newkvl3 = []
		for x in kvl3:
			if x < 0:
				newkvl3.append(x + 256)
			else:
				newkvl3.append(x)
		inv3=decode_nbt(bytes(newkvl3))
		for tagl in inv3.tags:
			for tagd in tagl.tags:
				try:
					items.append(tagd)
				except:
					''
	except:
		''
	try:
		kvl4 = playerData['player']['stats']['Pit']['profile']['spire_stash_inv']['data']
		newkvl4 = []
		for x in kvl4:
			if x < 0:
				newkvl4.append(x + 256)
			else:
				newkvl4.append(x)
		inv4=decode_nbt(bytes(newkvl4))
		for tagl in inv4.tags:
			for tagd in tagl.tags:
				try:
					items.append(tagd)
				except:
					''
	except:
		pass

	for i, item in enumerate(items):
		items[i] = unpack_nbt(item)

	return items

pageAt = 0
while pageAt < 4000:
	#try:
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
				print(f'checking {playerUsername}')
				checkPlayer(playerUsername)
		else:
			pass
	else:
		pass
	#except:
	#	pass

print('done')