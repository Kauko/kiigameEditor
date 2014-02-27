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
		#self.parseObjects()
		#self.parseTexts()
		
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
				#print ("%s not found" %(objectId))
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
			
		with open(self.dataDir + "/objects.json", encoding='utf-8') as f:
			objects = json.load(f)
			f.close()
			
		roomImages = {}
		objectsByCat = {}
		for child in images["children"]:
			objectCategory = child["attrs"]["category"]
			
			# Accept only certain types of views
			allowedViews = ("start", "end", "sequence", "room")
			if not (objectCategory in allowedViews):
				continue
				
			objectId = child["attrs"]["id"]
			
			if not (objectCategory in objectsByCat):
				objectsByCat[objectCategory] = {}
				
			layerAttrs = None
			layerChildren = None
			for layer in child:
				if (layer == "attrs"):
					layerAttrs = child[layer]
					
				elif (layer == "children"):
					layerChildren = child[layer]
			print("===\n\n")
			print("Here's layer attrs:")
			print(layerAttrs)
			#print(layerChildren)
				#print(child[layer], layer)
	
			
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
					
				# Merge object attributes
				elif (itemId in objects):
					jsonObject = item["attrs"]
					tempObject = objects[itemId]
					
					for attr in tempObject:
						jsonObject[attr] = tempObject[attr]
						
				# No object.json relation
				elif not (itemId in objects):
					jsonObject = item["attrs"]
				
				createdObjects[itemId] = jsonObject
			objectsByCat[objectCategory][objectId] = createdObjects
			
		import pprint
		pp = pprint.PrettyPrinter(indent=4)
		pp.pprint(objectsByCat)	
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
