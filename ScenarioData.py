# -*- coding: UTF-8 -*-

import json
import View, Object

class ScenarioData(object):
	def __init__(self):
		self.texts = {}
		self.roomList = []
		self.objectList = []
		self.sequenceList = []
		self.characterImages = []
		self.menuView = None
		self.endView = None
		self.dataDir = "gamedata"

	# Load and parse game data files
	def loadScenario(self):
		self.parseTexts()
		self.parseImages()
		#self.createInteractions()
		
	def parseTexts(self):
		with open(self.dataDir + "/texts.json", encoding='utf-8') as f:
			self.texts = json.load(f)
			f.close()
				
	def parseImages(self):
		with open(self.dataDir + "/images.json", encoding="utf-8") as f:
			images = json.load(f)
			f.close()
			
		with open(self.dataDir + "/objects.json", encoding='utf-8') as f:
			objects = json.load(f)
			f.close()
			
		objectsByCat = {}
		
		for child in images["children"]:
			objectCategory = child["attrs"]["category"]
			
			# Accept only certain types of views
			allowedViews = ("start", "end", "sequence", "room", "room_background")
			if not (objectCategory in allowedViews):
				continue
				
			objectId = child["attrs"]["id"]
			
			if not (objectCategory in objectsByCat):
				objectsByCat[objectCategory] = {}
				
			layerChildren = None
			for layer in child:
				if (layer == "children"):
					layerChildren = child[layer]
				elif (layer == "attrs"):
					layerAttrs = child[layer]
			#print("===\n\n")
			#print("Here's layer attrs:")
			#print(layerAttrs)
			#print(layerChildren)
			
			if not (layerChildren):
				continue
				
			# Go through objects in layers
			# And check for relation with objects.json objects
			createdObjects = {}
			for item in layerChildren:
				itemId = item["attrs"]["id"]
				jsonImage = item["attrs"]
				
				# Get possible attributes from objects.json
				if ("object_name" in item["attrs"]):
					itemId = item["attrs"]["object_name"]
					
					# Save related objects for later use
					jsonObject = objects[itemId]
					jsonObject["id"] = itemId
					
				elif (itemId in objects):
					jsonObject = objects[itemId]
					
				elif not (itemId in objects):
					jsonObject = {}
					
				jsonImage["classname"] = item["className"]
				
				if not (itemId in createdObjects):
					createdObjects[itemId] = {}
				createdObjects[itemId]["object"] = jsonObject
				
				if not ("image" in createdObjects[itemId]):
					createdObjects[itemId]["image"] = []
					
				createdObjects[itemId]["image"].append(jsonImage)
				
			objectsByCat[objectCategory][objectId] = createdObjects
		
		import pprint
		pp = pprint.PrettyPrinter(indent=4)
		pp.pprint(objectsByCat)
		
		# Create room objects
		for layer in objectsByCat["room_background"]["background_layer"]:
			room = objectsByCat["room_background"]["background_layer"][layer]
			viewAttributes = room["object"]
			imageAttributes = room["image"]
			
			roomObject = View.Room(viewAttributes, imageAttributes)
			self.roomList.append(roomObject)
			
		print("Rooms created:", len(self.roomList))
		
		# Create objects from the gathered data		
		for layer in objectsByCat:
			if (layer == "room"):
				for child in objectsByCat[layer]:
					
					currentRoom = self.getRoom(child[13:])
					
					for obj in objectsByCat[layer][child]:
						obj = objectsByCat[layer][child][obj]
						objectAttributes = obj["object"]
						imageAttributes = obj["image"]
						
						#print(obj)
						#print("\n")
						#objId = obj["id"]
						
						# Check category from either image or object
						try:
							objCat = obj["image"][0]["category"]
						except KeyError:
							objCat = obj["object"]["category"]
						
						if (objCat == "object" and obj["image"][0]["classname"] == "Text"):
							self.addText(currentRoom, imageAttributes)
							
						elif (objCat == "object"):
							self.addObject(currentRoom, objectAttributes, imageAttributes)
						# TODO: Secret items - fix it in kiigame first
						elif (objCat == "item"):
							self.addItem(currentRoom, objectAttributes, imageAttributes)
							
						elif (objCat == "container"):
							self.addContainer(currentRoom, objectAttributes, imageAttributes)
							
						elif (objCat == "door"):
							self.addDoor(currentRoom, objectAttributes, imageAttributes)
							
						elif (objCat == "obstacle"):
							self.addObstacle(currentRoom, objectAttributes, imageAttributes)
			
			elif (layer == "sequence"):
				for child in objectsByCat[layer]:
					imageAttributes = []
					
					# Ugly way to get sequenceId
					for sequenceId in objectsByCat[layer][child]:
						pass
						
					objectAttributes = objectsByCat[layer][child][sequenceId]["object"]
					objectAttributes["id"] = sequenceId
					imageAttributes = objectsByCat[layer][child][sequenceId]["image"]
					
					self.addSequence(objectAttributes, imageAttributes)
				
			elif (layer == "start"):
				start = objectsByCat[layer]["start_layer"]
				self.addMenu(start["begining"]["image"], start["start"]["image"], start["start_game"]["image"], start["start_credits"]["image"], start["start_empty"]["image"])
					
			elif (layer == "end"):
				endText = objectsByCat[layer]["end_layer"].pop("rewards_text", None)
				endImages = list(objectsByCat[layer]["end_layer"].values())
				
				self.addEnd(endText, endImages)
				
		print(self.roomList)
		
		for obj in self.objectList:
			obj.postInit(self.hello)
			
	def hello(self,x):
		print("x iss ",x)
	# Save scenario to JSON files
##	def saveScenario(self):
##		for item in self.objectList:
##			print (item)
		
	# Add interactions for pickable items
	def createInteractions(self):
		for item in self.objectList:
			if (type(item) != Object.Item):
				continue
				
			# Get other items with this item as their target
			for target in self.objectList:
				#print("    ",target.id)
				targetType = type(target)
				
				# Set trigger types
				if (targetType == Object.Item):
					if (target.interaction.triggerTarget == item.id):
						item.interaction.setTriggerType("triggerTo", 
						target.id, target.interaction.triggerOutcome)
						
				elif (targetType == Object.Container):
					if (target.key == item.id):
						item.interaction.setTriggerType("keyTo", target.id)
					elif (target.inItem == item.id):
						item.interaction.setTriggerType("goesInto", target.id)
					elif (target.outItem == item.id):
						item.interaction.comesFrom = target.id
						
				elif (targetType == Object.Door):
					if (target.key == item.id):
						item.interaction.setTriggerType("keyTo", target.id)
						
				elif (targetType == Object.Obstacle):
					if (target.trigger == item.id):
						item.interaction.setTriggerType("triggerTo", target.id)
					
	def getRoom(self, roomId):
		for room in self.roomList:
			if (room.id == roomId):
				return room

	def getSequence(self, sequenceId):
		for sequence in self.sequenceList:
			if (sequence.id == sequenceId):
				return sequence

	def getObject(self, objectId):
		for obj in self.objectList:
			if (obj.id == objectId):
				return obj

	def deleteObject(self, objectId):
		for obj in self.objectList:
			if obj.id == objectId:
				self.objectList.remove(obj)

		for room in self.roomList:
			roomObject = room.getObject(objectId)
			if (roomObject):
				room.deleteObject(objectId)
					
	def addEnd(self, endText, endImages):
		newView = View.End(endText, endImages)
		self.endView = newView
		
	def addMenu(self, beginningImage, background, startButton, creditsButton, emptyButton):

		
		newView = View.Menu(beginningImage, background, startButton, creditsButton, emptyButton)
		
		self.menuView = newView
		
	def addSequence(self, objectAttributes, imageAttributes):
		newView = View.Sequence(objectAttributes, imageAttributes)
		self.sequenceList.append(newView)

	# Create new generic object
	def addObject(self, room, objectAttributes, imageAttributes):
		newObject = Object.Object(room, objectAttributes, imageAttributes)
		self.__appendObject__(newObject, room)

	def addText(self, room, objectAttributes):
		newObject = Object.JSONText(objectAttributes)
		self.__appendObject__(newObject, room)

	# Create new item
	def addItem(self, room, objectAttributes, imageAttributes):
		newObject = Object.Item(room, objectAttributes, imageAttributes)
		self.__appendObject__(newObject, room)

	# Create new container
	def addContainer(self, room, objectAttributes, imageAttributes):
		newObject = Object.Container(room, objectAttributes, imageAttributes)
		self.__appendObject__(newObject, room)

	# Create new door
	def addDoor(self, room, objectAttributes, imageAttributes):
		newObject = Object.Door(room, objectAttributes, imageAttributes)	
		self.__appendObject__(newObject, room)

	# Create new obstacle
	def addObstacle(self, room, objectAttributes, imageAttributes):
		newObject = Object.Obstacle(room, objectAttributes, imageAttributes)
		self.__appendObject__(newObject, room)

	# Add newly created object to this instance's and room's object lists
	def __appendObject__(self, newObject, room=None):
		# Object may be created without a room
		if (room):
			newObject.location = room
			room.objectList.append(newObject)
			
		self.objectList.append(newObject)
		
	def deleteView(self):
		return

	def editObject(self):
		return

	def editUse(self):
		return

sc = ScenarioData()
sc.loadScenario()
#sc.saveScenario()

