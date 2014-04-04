# -*- coding: UTF-8 -*-

import json, View, Object
from collections import OrderedDict
from os.path import dirname, abspath

class ScenarioData(object):
	def __init__(self):
		self.texts = OrderedDict()
		self.roomList = []
		self.sequenceList = []
		self.customObjectList = []
		self.miscObjects = []
		self.startView = None
		self.endViewList = []
		self.menuList = []
		
		self.dataDir = dirname(abspath(__file__))+"/gamedata/latkazombit"
		
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
		with open(self.dataDir + "/images.json", encoding='utf-8') as f:
			images = json.load(f)
			f.close()
			
		with open(self.dataDir + "/objects.json", encoding='utf-8') as f:
			objects = json.load(f)
			f.close()
			
		# Parse objects from images.json and objects.json into categorized dict
		objectsByCat = OrderedDict()
		for child in images["children"]:
			layerObject = {}
			if ("object_name" in child["attrs"]):
				layerObject = objects[child["attrs"]["object_name"]]
				
			objectCategory = child["attrs"]["category"]
			objectId = child["attrs"]["id"]
			
			if not (objectCategory in objectsByCat):
				objectsByCat[objectCategory] = OrderedDict()
								
			# Leave misc objects as they are
			if (objectCategory == "misc"):
				self.miscObjects.append(child)
				continue
			    
			layerChildren = None
			for layer in child:
				if (layer == "children"):
					layerChildren = child[layer]
				elif (layer == "attrs"):
					layerAttrs = child[layer]
			
			if not (layerChildren):
				continue
			    
			# Go through the objects in the layer
			# And check for relation with objects.json objects
			createdObjects = OrderedDict()
			for item in layerChildren:
				itemId = item["attrs"]["id"]
				jsonImage = item["attrs"]
				
				# Get possible attributes from objects.json
				if ("object_name" in item["attrs"]):
					itemId = item["attrs"]["object_name"]
					
					try:
						jsonObject = objects[itemId]
					except KeyError:
						print("Warning: Could not find object.json object for '%s' (object_name -> '%s')" %(item["attrs"]["id"], itemId))
					
				elif (itemId in objects):
					jsonObject = objects[itemId]
					
				elif not (itemId in objects):
					jsonObject = {}
				
				# Create dict key for the item
				if not (itemId in createdObjects):
					createdObjects[itemId] = {}
					
				createdObjects[itemId]["object"] = jsonObject
				createdObjects[itemId]["className"] = item["className"]
				
				if not ("image" in createdObjects[itemId]):
					createdObjects[itemId]["image"] = []
				
				createdObjects[itemId]["image"].append(jsonImage)

            # Compose the final dict key and values				
			objectsByCat[objectCategory][objectId] = {}
			objectsByCat[objectCategory][objectId]["image"] = createdObjects
			objectsByCat[objectCategory][objectId]["object"] = layerObject
			objectsByCat[objectCategory][objectId]["attrs"] = child["attrs"]
			objectsByCat[objectCategory][objectId]["className"] = child["className"]
			
		#import pprint
		#pp = pprint.PrettyPrinter(indent=4)
		#pp.pprint(objectsByCat)
		
		# Create objects from the categorized dict
		for layer in objectsByCat:
			if (layer == "misc"):
				continue
				
			for child in objectsByCat[layer]:
				viewImages = objectsByCat[layer][child].pop("image")
				viewAttributes = objectsByCat[layer][child]
				
				if (layer == "room"):
					self.addRoom(child, viewAttributes, viewImages)
				elif (layer == "sequence"):
					self.addSequence(child, viewAttributes, viewImages)
				elif (layer == "start"):
					self.addStart(viewAttributes, viewImages)
				elif (layer == "end"):
					self.addEnd(viewAttributes, viewImages)
				elif (layer == "menu"):
					self.addMenu(child, viewAttributes, viewImages)
				elif (layer == "custom"):
					self.addCustomView(child, viewAttributes, viewImages)
					
		# Post-init sets triggers, outcomes etc.
		for obj in self.roomList + self.endViewList:
			obj.postInit(self.getGameObject)
			
		self.startView.postInit(self.getGameObject)
		
	# Save scenario to JSON files
	def saveScenario(self):
		scenarioTexts = {}
		scenarioObjects = {}
		scenarioImages = []
		
		# Go through views
		for view in self.roomList + self.sequenceList + [self.startView] + self.endViewList + self.menuList + self.customObjectList:
			viewChildren = []
			
			# Contents for objects.json from view
			if ("object_name" in view.attrs):
				scenarioObjects[view.attrs["object_name"]] = view.object
			
			# Go through objects inside views
			for viewChild in view.getChildren():
				childJSON = viewChild.objectAttributes
				
				# Go through images inside objects
				for childImage in viewChild.images:
					viewChildren.append(self.__createLayerChildJSON__(childImage.imageAttributes, childImage.getClassname()))
					
					# Contents for objects.json from image
					if ("object_name" in childImage.imageAttributes):
						scenarioObjects[childImage.imageAttributes["object_name"]] = childImage.objectAttributes["object"]
						
				if (type(viewChild) == Object.JSONImage):
					viewChildren.append(self.__createLayerChildJSON__(viewChild.imageAttributes, viewChild.getClassname()))
					
			layerJSON = self.__createLayerJSON__(view.attrs, viewChildren, view.classname)
			scenarioImages.append(layerJSON)
			
		# Go through self.texts and add modified texts from objects
		objects = self.getAllObjects()[0]
		for object in objects:
			for objectImage in object.getImages():
				if (objectImage.id in self.texts):
					self.texts[objectImage.id] = objectImage.texts
		
		# Miscellaneous objects
		for misc in self.miscObjects:
			scenarioImages.append(misc)
		
		# Bundle everything together
		scenarioAttrs = {"id": "Stage", "width": 981, "height": 643}
		scenarioChildren = self.__createLayerJSON__(scenarioAttrs, scenarioImages, "Stage")
		
		textsJSON = json.dumps(self.texts, ensure_ascii=False, sort_keys=True, indent=4, separators=(',', ': '))
		imagesJSON = json.dumps(scenarioChildren, sort_keys=True, indent=4, separators=(',', ': '))
		objectsJSON = json.dumps(scenarioObjects, sort_keys=True, indent=4, separators=(',', ': '))
		
		#print(textsJSON)
		#print(imagesJSON)
		#print(objectsJSON)
		
		# Save into file
		#f = open(self.dataDir + "/texts_lol.json", "w", encoding='utf-8')
		#f.write(textsJSON)
		#f.close()

		#f = open(self.dataDir + "/images.json", "w")
		#f.write(imagesJSON)
		#f.close()
		
		#f = open(self.dataDir + "/objects.json", "w")
		#f.write(objectsJSON)
		#f.close()
		
	# Game object layers
	def __createLayerJSON__(self, attrs, children, className="Layer"):
		return {"attrs": attrs, "className": className, "children": children}
	
	# Single items for game layers
	def __createLayerChildJSON__(self, attrs, className="Image"):
		return {"attrs": attrs, "className": className}
		
	def getRoom(self, roomId):
		for room in self.roomList:
			if (room.id == roomId):
				return room
	
	def getRooms(self):
		return self.roomList
	
	def getRoomBackLoc(self, i):
		room = self.roomList[i]
		loc = self.dataDir + '/' + room.background.imageAttributes['src']
		return loc

	def getSequence(self, sequenceId):
		for sequence in self.sequenceList:
			if (sequence.id == sequenceId):
				return sequence

	def getObject(self, objectId):
		for room in self.roomList:
			for obj in room.objectList:
				if (obj.id == objectId):
					return obj

	def getJSONObject(self, imageId):
		objects = self.getAllObjects()[0]
		for obj in objects:
			images = obj.getImages()
			for img in images:
				if (img.id == imageId):
					return img
					
	def getCustomObject(self, objectId):
		for obj in self.customObjectList:
			if (obj.id == objectId):
				return obj
	# Get given types of objects found in rooms
	def getObjectsByType(self, objectType):
		retObjects = []
		for room in self.roomList:
			roomObjects = {"room": room, "objects": []}
			for item in room.getItems():
				if (item.__class__.__name__.lower() == objectType):
					roomObjects["objects"].append(item)
			if (len(roomObjects["objects"]) != 0):
				retObjects.append(roomObjects)
		return retObjects		
		
	def getGeneralName(self, objectType):
		objectType = objectType.lower()
		if (objectType == "object"):
			return Object.Object.generalName
		elif (objectType == "item"):
			return Object.Item.generalName
		elif (objectType == "door"):
			return Object.Door.generalName
		elif (objectType == "container"):
			return Object.Container.generalName
		elif (objectType == "obstacle"):
			return Object.Obstacle.generalName
			
	# Get room, sequence or other object
	def getGameObject(self, objectType, objectId):
		objectType = objectType.lower()
		
		if (objectType == "room"):
			return self.getRoom(objectId)
		elif (objectType == "sequence"):
			return self.getSequence(objectId)
		elif (objectType == "object"):
			return self.getObject(objectId)
		elif (objectType == "menu"):
			return self.getMenu(objectId)
		elif (objectType == "custom"):
			return self.getCustomObject(objectId)
			
	# Get all right type of objects, amount of images and secrets,
	def getAllObjects(self):
		retObjects = []
		imgCount = 0
		secretCount = 0
		rightTypes = ["Object", "Item", "Container", "Door", "Obstacle"]
		
		for room in self.roomList:
			for object in room.getItems():
				if (object.__class__.__name__ in rightTypes and object.getClassname() != "Text"):
						retObjects.append(object)
						imgCount += len(object.getImages())
						if (object.getRepresentingImage().imageAttributes["category"] == "secret"):
							secretCount += 1
					
		return [retObjects, imgCount, secretCount]

	def getMenu(self, menuId):
		for menu in self.menuList:
			if (menu.id == menuId):
				return menu
				
	def deleteObject(self, objectId):
		for obj in self.objectList:
			if obj.id == objectId:
				self.objectList.remove(obj)

		for room in self.roomList:
			roomObject = room.getObject(objectId)
			if (roomObject):
				room.deleteObject(objectId)
				
	def addEnd(self, endAttributes, endImages):
		newView = View.End(self.texts, endAttributes, endImages)
		self.endViewList.append(newView)
		
	def addStart(self, startAttributes, startImages):
		newView = View.Start(self.texts, startAttributes, startImages)
		self.startView = newView
		
	def addSequence(self, sequenceId, sequenceAttributes, sequenceImages):
		newView = View.Sequence(self.texts, sequenceId, sequenceAttributes, sequenceImages)
		self.sequenceList.append(newView)

	def addRoom(self, roomId, roomAttributes, roomImages):
		newView = View.Room(self.texts, roomId, roomAttributes, roomImages)
		self.roomList.append(newView)
		
	def addCustomView(self, viewId, viewAttributes, viewImages):
		newView = View.Custom(self.texts, viewId, viewAttributes, viewImages)
		self.customObjectList.append(newView)
		
	def addMenu(self, menuId, menuAttributes, menuImages):
		newView = View.Menu(self.texts, menuId, menuAttributes, menuImages)
		self.menuList.append(newView)
		
	def deleteView(self):
		return

	def editObject(self):
		return

	def editUse(self):
		return

if (__name__ == "__main__"):
	sc = ScenarioData()
	sc.loadScenario()
	sc.saveScenario()

