# -*- coding: cp1252 -*-

import json
import View, Object

class ScenarioData(object):
	def __init__(self):
		self.roomList = []
		self.objectList = []
		self.sequenceList = []
		self.characterImages = []
		self.menuView = None
		self.endView = None
		self.dataDir = "gamedata"

	# Load and parse game data files
	def loadScenario(self):
		self.parseImages()
		self.parseObjects()
		self.parseTexts()
		
	def parseObjects(self):
		with open(self.dataDir + "/objects.json", encoding='utf-8') as f:
			objects = json.load(f)
			f.close()
			
		for objectId in objects:
			curObject = objects[objectId]
			objectType = curObject["category"]
			
			# The object may be already created image, room or sequence.
			# Find it and add attributes from objects.json
			foundObject = None
			for listItem in self.objectList:
				if (listItem.id == objectId):
					foundObject = listItem
					break
			
			if not (foundObject):
				for listItem in self.roomList:
					if (listItem.id == objectId):
						foundObject = listItem
						
			if not (foundObject):
				for listItem in self.sequenceList:
					if (listItem.id == objectId):
						foundObject = listItem
						break
						
			# Check menuview
			if not (foundObject):
				print(self.menuView.background.id, objectId)
				if (self.menuView.background.id == objectId):
					print ("ASLDOADL")
			#print (self.menuView)
			if not (foundObject):
				print ("%s not found" %(objectId))
				continue
			if (objectType == "item"):
				pass			
			elif (objectType == "container"):
				item = Object.Door(objectId)
			elif (objectType == "door"):
				item = Object.Obstacle(objectId)
			elif (objectType == "obstacle"):
				item = Object.Item(objectId)
			elif (objectType == "secret"):
				item = Object.Item(objectId)
				item.isSecret = True
			elif (objectType == "object"):
				item = Object.Object(objectId)
			
	def parseTexts(self):
		with open(self.dataDir + "/texts.json", encoding='utf-8') as f:
			texts = json.load(f)
			f.close()
			
	def parseImages(self):
		with open(self.dataDir + "/images.json", encoding="utf-8") as f:
			images = json.load(f)
			f.close()
			
		roomImages = {}
		for child in images["children"]:
			id = child["attrs"]["id"]
			category = child["attrs"]["category"]
			
			# Start menu
			if (id == "start_layer"):
				self.menuView = View.Menu("start_layer")
				self.menuView.name = "Alkuvalikko"
				
				for image in child["children"]:
					image_id = image["attrs"]["id"]
					
					if (image_id == "start"):
						self.menuView.background = Object.JSONObject(image["attrs"])
						
					elif (image_id == "begining"):
						self.menuView.startImage = Object.JSONObject(image["attrs"])
						
					elif (image_id == "start_game"):
						startButton = Object.Object("start_game")
						startButton.name = "Aloituspainike"
						startButton.image = Object.JSONObject(image["attrs"])
						self.menuView.startButton = startButton
						
					elif (image_id == "start_credits"):
						creditsButton = Object.Object("start_credits")
						creditsButton.name = "Tekijät-painike"
						creditsButton.image = Object.JSONObject(image["attrs"])
						self.menuView.creditsButton = creditsButton
						
					elif (image_id == "start_empty"):
						emptyButton = Object.Object("start_empty")
						emptyButton.name = "Tyhjä painike"
						emptyButton.image = Object.JSONObject(image["attrs"])
						self.menuView.creditsButton = creditsButton
						
			# End images
			elif (id == "end_layer"):
				endView = View.End("end_layer")
				endView.name = "Loppukuva"
				
				for image in child["children"]:
					image_id = image["attrs"]["id"]
					
					if (image_id.find("end_picture_") != -1):
						picture = Object.JSONObject(image["attrs"])
						endView.endPictures.append(picture)
						
					elif (image_id == "rewards_text"):
						endView.endText = Object.JSONObject(image["attrs"], "Text")
				self.endView = endView
				
			# Store background layer images to a temporary dict
			elif (id == "background_layer"):	
				# TODO: This is stupid
				for image in child["children"]:
					roomId = image["attrs"]["id"]
					picture = View.Room(roomId)
					roomImages[roomId] = picture
					
			# TODO: Character layer
			elif (id == "character_layer"):
				pass
						
			elif (category == "sequence"):
				sequence = View.Sequence(child["attrs"]["id"])
				
				for image in child["children"]:
					image =  Object.JSONObject(image["attrs"])
					sequence.images.append(image)
					
				self.sequenceList.append(sequence)
				
			# Use the temporary dict here to get room objects
			elif (id.find("object_layer_") != -1):
				# For some reason this room may not exist
				try:
					room = roomImages[id[13:]]
				except KeyError:
					continue
					
				# Create room objects
				for image in child["children"]:
					objectType = image["attrs"]["category"]
					objectId = image["attrs"]["id"]
					
					if (objectType == "item"):
						item = Object.Item(objectId)
					elif (objectType == "container"):
						item = Object.Door(objectId)
					elif (objectType == "door"):
						item = Object.Obstacle(objectId)
					elif (objectType == "obstacle"):
						item = Object.Item(objectId)
					elif (objectType == "secret"):
						item = Object.Item(objectId)
						item.isSecret = True
					elif (objectType == "object"):
						item = Object.Object(objectId)
						
					picture =  Object.JSONObject(image["attrs"])
					room.objectList.append(item)
					self.objectList.append(item)
					
				self.roomList.append(room)
				
		return

	def saveScenario(self):
		return

	def addView(self):
		return

	def addObject(self):
		return

	def deleteView(self):
		return

	def deleteObject(self):
		return

	def getObject(self):
		return

	def getView(self):
		return

	def editObject(self):
		return

	def editUse(self):
		return

sc = ScenarioData()
sc.loadScenario()
