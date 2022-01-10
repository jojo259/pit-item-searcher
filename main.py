import requests
import time
import nbt
import io
import math
from nbt.nbt import NBTFile, TAG_Long, TAG_Int, TAG_String, TAG_List, TAG_Compound

apiKey = ''
try:
	apiKey = open('apiKey.txt').read()
except:
	print('\nerror, create text file "apiKey" with your hypixel api key\nexiting')
	exit()

def checkItem(curItem):
	itemName = getVal(curItem, ['tag','display','Name']) #item's name e.g. '§9Tier III Blue Pants'. use itemName[2:] to remove the color coding at the start or just use like <if 'Dark' in itemName> if ur lazy
	itemCount = getVal(curItem, ['count']) #how many there are, e.g. half a stack of vile = 32. will be left as None i think if the item is unstackable (integer)
	itemEnchants = getVal(curItem, ['tag','ExtraAttributes','CustomEnchants']) #list of enchants in {'Key': <enchantKeyString>, 'Level': <levelInteger>} dict format
	itemNonce = getVal(curItem, ['tag','ExtraAttributes','Nonce']) #item's nonce (integer)
	itemLives = getVal(curItem, ['tag','ExtraAttributes','Lives']) #current lives (integer)
	itemMaxLives = getVal(curItem, ['tag','ExtraAttributes','MaxLives']) #maximum lives (integer)
	itemTier = getVal(curItem, ['tag','ExtraAttributes','UpgradeTier']) #current tier (0, 1, 2, 3) (integer)
	itemGemmed = getVal(curItem, ['tag','ExtraAttributes','UpgradeGemsUses']) #gemmed status. None if not gemmed, 1 (integer) if gemmed
	
	if itemName != None: #avoids checking empty inventory slots
		toOutput = False

		if 'Dark' in itemName: #currently checks for dark pants with 150+ lives
			if itemMaxLives >= 150:
				toOutput = True

		if toOutput:
			print()
			print(f'writing {itemName} to output.txt')
			print()
			open('output.txt', 'a', encoding = 'UTF-8').write(str(curItem) + '\n\n')

def checkPlayer(playerUsername):
	toCheckUrl = f'https://api.hypixel.net/player?key={apiKey}&name={playerUsername}'
	dataReceived = doRequest(toCheckUrl)
	print(f'checking {playerUsername}')
	#try:
	playerItems = getItems(dataReceived)
	for item in playerItems:
		item['ownerUuid'] = dataReceived['player']['uuid']
		item['owner'] = playerUsername
		checkItem(item)
	#except:
	#	print(f'error when checking {playerUsername}')

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

	toDecode.append(getVal(playerData, ['player','stats','Pit','profile','inv_contents','data'])) #inventory
	toDecode.append(getVal(playerData, ['player','stats','Pit','profile','inv_enderchest','data'])) #enderchest
	toDecode.append(getVal(playerData, ['player','stats','Pit','profile','item_stash','data'])) #stash
	toDecode.append(getVal(playerData, ['player','stats','Pit','profile','spire_stash_inv','data'])) #spire stash
	toDecode.append(getVal(playerData, ['player','stats','Pit','profile','inv_armor','data'])) #armor
	toDecode.append(getVal(playerData, ['player','stats','Pit','profile','mystic_well_item','data'])) #mystic well item
	toDecode.append(getVal(playerData, ['player','stats','Pit','profile','mystic_well_pants','data'])) #mystic well pants
	
	for curDecode in toDecode:
		if curDecode != None:
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
							items.append(unpacked)
					except:
						pass

	return items

def getVal(theDict, thePath):
	try:
		for i in range(len(thePath)):
			theDict = theDict[thePath[0]]
			thePath.pop(0)
		return theDict
	except:
		return None

def doRequest(url):
	while True:
		try:
			apiCalled = requests.get(url, timeout = 10).json()
			if apiCalled['success']:
				return apiCalled
			else:
				print('api error, probably throttled, retrying')
				time.sleep(1)
		except:
			print('api error, probably timeout, retrying')
			time.sleep(1)

print('starting')

pageAt = int(input('What page of XP leaderboards to start at?\n'))

open('output.txt', 'a', encoding = 'UTF-8').write(f'\n---\nNEW SEARCH FROM {pageAt}\n---\n')

while pageAt < 9999:
	#try:
	print(f'page {pageAt}')
	lbPlayers = doRequest(f'https://pitpanda.rocks/api/leaderboard/xp?page={pageAt}')
	print(f'got leaderboard page {pageAt}')
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
		break #finished checking all leaderboards
	#except:
	#	print(f'error when checking leaderboards page {pageAt}')

print('done')

open('output.txt', 'a', encoding = 'UTF-8').write(f'\n---\nFINISHED SEARCH\n---\n')