# -*- coding: cp1252 -*-

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
				
				# In-attribute relation with images.json objects ("object_name")
				if ("object_name" in item["attrs"]):
					jsonObject = objects[item["attrs"]["object_name"]]
					
					# Insert images.json object attributes on object.json object
					for attr in jsonObject:
						if (jsonObject[attr] == itemId):
							jsonObject[attr] = item["attrs"]
							break
							
					itemId = item["attrs"]["object_name"]
					jsonObject["id"] = itemId
					
				# Merge object attributes
				elif (itemId in objects):
					jsonObject = item["attrs"]
					tempObject = objects[itemId]
					
					for attr in tempObject:
						jsonObject[attr] = tempObject[attr]
						
				# No object.json relation
				elif not (itemId in objects):
					jsonObject = item["attrs"]
					
				jsonObject["classname"] = item["className"]
				
				createdObjects[itemId] = jsonObject
			objectsByCat[objectCategory][objectId] = createdObjects
			
		import pprint
		pp = pprint.PrettyPrinter(indent=4)
		
		pp.pprint(objectsByCat)
		
		# Create room objects
		for layer in objectsByCat["room_background"]["background_layer"]:
			attrs = objectsByCat["room_background"]["background_layer"][layer]
			roomObject = View.Room(layer)
			
			try:
				roomObject.music = attrs["music"]
			except:
				roomObject.music = ""
				
			self.roomList.append(roomObject)
			
		print("Rooms created:", len(self.roomList))
		
		# Create objects from the gathered data		
		for layer in objectsByCat:		
			if (layer == "room"):
				for child in objectsByCat[layer]:
					
					currentRoom = self.getRoom(child[13:])
					
					for obj in objectsByCat[layer][child]:
						obj = objectsByCat[layer][child][obj]
						
						#print(obj)
						#print("\n")
						objId = obj["id"]
						
						if (obj["category"] == "object"):
							self.addObject(currentRoom, obj["id"])
							#gameObject = Object.Object(obj["id"])
							
						# TODO: Secret items - fix it in kiigame first
						elif (obj["category"] == "item"):
							self.addItem(currentRoom, obj["id"])
							#gameObject = Object.Item(obj["id"])
							
						elif (obj["category"] == "container"):
							self.addContainer(currentRoom, obj["id"], obj["locked"])
							#gameObject = Object.Container(obj["id"])
							#gameObject.locked = obj["locked"]
						elif (obj["category"] == "door"):
							self.addDoor(currentRoom, obj["id"])
							#gameObject = Object.Door(obj["id"])
							
						elif (obj["category"] == "obstacle"):
							self.addObstacle(currentRoom, obj["id"])
							#gameObject = Object.Obstacle(obj["id"])
							
						
						# TODO: Better parameters for addX functions
						# 		General (image, location) and object-specific (name, key, ...)
						
						# Common attributes for Objects
						#try:
						#	objectName = self.texts[obj["id"]]["name"]
						#except KeyError:
						#	objectName = ""
							
						# TODO: Name giving
						#gameObject.name = objectName
						#gameObject.image = Object.JSONObject(obj)
						
						
						#currentRoom.objectList.append(obj)
						
			elif (layer == "sequence"):
				pass
			elif (layer == "start"):
				pass
			elif (layer == "end"):
				pass
		print(self.roomList)
		return

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

	def saveScenario(self):
		return

	def addView(self):
		return

	# Create new generic object
	def addObject(self, room, objectId):
		newObject = Object.Object(objectId)
		
		self.__appendObject__(newObject, room)

	# Create new item
	def addItem(self, room, itemId, isSecret=False):
		newObject = Object.Object(itemId)
		newObject.isSecret = isSecret
		
		self.__appendObject__(newObject, room)

	# Create new container
	def addContainer(self, room, containerId, isLocked):
		newObject = Object.Container(containerId)
		newObject.isLocked = isLocked

		self.__appendObject__(newObject, room)

	# Create new door
	def addDoor(self, room, doorId):
		newObject = Object.Door(doorId)

		self.__appendObject__(newObject, room)

	# Create new obstacle
	def addObstacle(self, room, obstacleId):
		newObject = Object.Obstacle(obstacleId)

		self.__appendObject__(newObject, room)

	# Add newly created object to this instance's and room's object lists
	def __appendObject__(self, newObject, room=None):
		# Object may be created without room
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
