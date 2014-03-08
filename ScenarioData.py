import json
import View
import Object

class ScenarioData(object):
	def __init__(self):
		self.texts = {}
		self.roomList = []
		self.objectList = []
		self.sequenceList = []
		#self.characterImages = []
		self.otherObjectsList = {}
		self.menuView = None
		self.endView = None
		self.dataDir = "gamedata/latkazombit"

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
			layerObject = {}
			if ("object_name" in child["attrs"]):
				layerObject = objects[child["attrs"]["object_name"]]
				
			objectCategory = child["attrs"]["category"]
			
			# Accept only certain types of views
			#allowedViews = ("start", "end", "sequence", "room", "room_background")
			#if not (objectCategory in allowedViews):
			#	continue
				
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
							
			# Leave misc objects as they are
			if (objectCategory == "misc"):
			    if not ("misc" in objectsByCat):
			        objectsByCat["misc"] = {}
			    objectsByCat["misc"][objectId] = child
			    continue
			    
			# Go through the objects in the layer
			# And check for relation with objects.json objects
			createdObjects = {}
			for item in layerChildren:
				itemId = item["attrs"]["id"]
				jsonImage = item["attrs"]
				
				# Get possible attributes from objects.json
				if ("object_name" in item["attrs"]):
					itemId = item["attrs"]["object_name"]
					jsonObject = objects[itemId]
					
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
			
		import pprint
		pp = pprint.PrettyPrinter(indent=4)
		pp.pprint(objectsByCat)
		
		# Create room objects from background_layer
		"""for layer in objectsByCat["room_background"]["background_layer"]:
			if (layer in ("attrs", "object")):
				continue
					
			room = objectsByCat["room_background"]["background_layer"][layer]
			viewAttributes = room["object"]
			imageAttributes = room["image"]
			
			self.addRoom(viewAttributes, imageAttributes[0])
			
		print("Rooms created:", len(self.roomList))
		"""
		# Create objects from the gathered data		
		for layer in objectsByCat:
			if (layer == "misc"):
				continue
				
			for child in objectsByCat[layer]:
				#print(objectsByCat[layer][child])
				viewImages = objectsByCat[layer][child].pop("image")
				viewAttributes = objectsByCat[layer][child]
				
				#for obj in objectsByCat[layer][child]:
					#obj = objectsByCat[layer][child][obj]
					#objectAttributes = obj["object"]
					#imageAttributes = obj["image"]
				#	viewImages.append(objectsByCat[layer][child][obj])
				"""
				# Check category from either image or object
				try:
					objCat = obj["image"][0]["category"]
				except KeyError:
					objCat = obj["object"]["category"]
				
				if (objCat == "room_background"):
					self.addRoom(viewAttributes, imageAttributes[0])
				
				elif (objCat == "object" and obj["image"][0]["classname"] == "Text"):
					self.addText(currentRoom, imageAttributes[0])
					
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
				"""
				#print("loooo",viewImages)
				if (layer == "room"):
					self.addRoom(child, viewAttributes, viewImages)
				elif (layer == "sequence"):
				    print("seqq")
				else:
				    print("other")
			"""		    
			elif (layer == "sequence"):
				for child in objectsByCat[layer]:
					sequenceAttrs = objectsByCat[layer][child].pop("attrs")
					objectsByCat[layer][child].pop("object")
					
					imageAttributes = []
					
					# Ugly way to get sequenceId
					for sequenceId in objectsByCat[layer][child]:
						pass
						
					objectAttributes = objectsByCat[layer][child][sequenceId]["object"]
					objectAttributes["id"] = sequenceId
					imageAttributes = objectsByCat[layer][child][sequenceId]["image"]
					
					self.addSequence(sequenceAttrs, objectAttributes, imageAttributes)
				
			elif (layer == "start"):
				start = objectsByCat[layer]["start_layer"]
				startAttributes = start["object"]
				
				self.addMenu(startAttributes, start["attrs"], start["begining"]["image"][0], start["start"]["image"][0], start["start_game"]["image"][0], start["start_credits"]["image"][0], start["start_empty"]["image"][0])
					
			elif (layer == "end"):
				endText = objectsByCat[layer]["end_layer"].pop("rewards_text", None)["image"][0]
				endAttrs = objectsByCat[layer]["end_layer"].pop("attrs")
				endObject = objectsByCat[layer]["end_layer"].pop("object")
				endImages = list(objectsByCat[layer]["end_layer"].values())
				
				endImagesList = []
				for image in endImages:
					endImagesList.append(image["image"][0])
					
				self.addEnd(endObject, endAttrs, endText, endImagesList)
				
			elif (layer == "misc" or layer == "custom"):
				for child in objectsByCat[layer]:
					
					self.otherObjectsList[child] = objectsByCat[layer][child]
			"""
		#pp.pprint(self.otherObjectsList)
		print(self.roomList)
		
		for obj in self.objectList:
			obj.postInit(self.getGameObject)
			
	# Save scenario to JSON files
	def saveScenario(self):
		scenarioObjects = {}
		scenarioChildren = []
		#TODO: Objects JSON, texts JSON
		# Start menu
		startObjects = []
		startObjects.extend([
			self.__createLayerChild__(self.menuView.beginingImage.objectAttributes),
			self.__createLayerChild__(self.menuView.background.objectAttributes),
			self.__createLayerChild__(self.menuView.startButton.objectAttributes),
			self.__createLayerChild__(self.menuView.creditsButton.objectAttributes),
			self.__createLayerChild__(self.menuView.emptyButton.objectAttributes)
		])
		startAttrs = self.menuView.layerAttrs
		startLayer = self.__createLayer__(startAttrs, startObjects)
		scenarioChildren.append(startLayer)
		
		try:
			scenarioObjects[startAttrs["object_name"]] = self.menuView.objectAttributes
		except KeyError:
			pass
			
		# End view
		endObjects = []
		endAttrs = self.endView.layerAttrs
		
		for image in self.endView.endImages:
			endObjects.append(self.__createLayerChild__(image.objectAttributes))
			
		endObjects.append(self.__createLayerChild__(self.endView.endText.objectAttributes, "Text"))
		
		endLayer = self.__createLayer__(endAttrs, endObjects)
		scenarioChildren.append(endLayer)
		
		scenarioObjects[self.endView.layerAttrs["object_name"]] = self.endView.objectAttributes
		
		# Sequences
		for sequence in self.sequenceList:
			sequenceObjects = []
			sequenceAttrs = sequence.layerAttrs
			
			for image in sequence.images:
				sequenceObjects.append(self.__createLayerChild__(image.objectAttributes))
				
			sequenceLayer = self.__createLayer__(sequenceAttrs, sequenceObjects)
			scenarioChildren.append(sequenceLayer)
			scenarioObjects[sequenceAttrs["object_name"]] = sequence.objectAttributes
			
		# Rooms
		backgroundChildren = []
		
		for room in self.roomList:
			roomObjects = []
			backgroundChildren.append(self.__createLayerChild__(room.background.objectAttributes))
			
			# Image JSONs from room objects
			for obj in room.objectList:
				objImages = obj.getImages()
				
				for image in objImages:
					objClassName = image.objectAttributes["classname"]
					roomObjects.append(self.__createLayerChild__(image.objectAttributes, objClassName))
					
				# Object JSONs can be created too
				objType = type(obj)
				if (objType == Object.Item):
					if (len(obj.objectAttributes) != 0):
						scenarioObjects[obj.id] = obj.objectAttributes
						
				elif (objType != Object.JSONText):
					if ("object_name" in obj.image.objectAttributes):
						scenarioObjects[obj.image.objectAttributes["object_name"]] = obj.objectAttributes
						
			roomLayer = self.__createLayer__(room.layerAttributes, roomObjects)
			scenarioChildren.append(roomLayer)				
			
			try:
				scenarioObjects[room.layerAttributes["object_name"]] = room.objectAttributes
			except KeyError:
				pass
		
		# Background layer
		backgroundLayerAttrs = {"id": "background_layer", "visible": False, "category": "room_background"}
		backgroundLayer = self.__createLayer__(backgroundLayerAttrs, backgroundChildren)
		scenarioChildren.append(backgroundLayer)
		
		# Other objects
		for obj in self.otherObjectsList:
			layerAttrs = self.otherObjectsList[obj].pop("attrs")
			layerObject = self.otherObjectsList[obj].pop("object")
			
			layerObjects = []
			for image in self.otherObjectsList[obj]:
				imageAttrs = self.otherObjectsList[obj][image]["image"][0]
				imageClassname = imageAttrs["classname"]
				
				layerObjects.append(self.__createLayerChild__(imageAttrs, imageClassname))
				#print(imageAttrs["object_name"])
				try:
					scenarioObjects[imageAttrs["object_name"]] = self.otherObjectsList[obj][image]["object"]
				except KeyError:
					pass
				
			otherLayer = self.__createLayer__(layerAttrs, layerObjects)
			scenarioChildren.append(otherLayer)
			
		# Bundle everything together
		scenarioAttrs = {"id": "Stage", "width": 981, "height": 643}
		scenarioData = self.__createLayer__(scenarioAttrs, scenarioChildren, "Stage")
		
		imagesJSON = json.dumps(scenarioData, sort_keys=True, indent=4, separators=(',', ': '))
		objectsJSON = json.dumps(scenarioObjects, sort_keys=True, indent=4, separators=(',', ': '))
		#print(imagesJSON)
		#print(objectsJSON)
		
		# Save into file
		#f = open(self.dataDir + "/images.json", "w")
		#f.write(imagesJSON)
		#f.close()
		
		#f = open(self.dataDir + "/objects.json", "w")
		#f.write(objectsJSON)
		#f.close()
		
	# Game object layers
	def __createLayer__(self, attrs, children, className="Layer"):
		return {"attrs": attrs, "className": className, "children": children}
	
	# Single items for game layers
	def __createLayerChild__(self, attrs, className="Image"):
		return {"attrs": attrs, "className": className}
		
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
	
	def getText(self, objectId):
		try:
			return self.texts[objectId]
		except KeyError:
			return None
		
	# Get room, sequence or object
	def getGameObject(self, entityType, entityId):
		if (entityType == "room"):
			return self.getRoom(entityId)
		elif (entityType == "sequence"):
			return self.getSequence(entityId)
		elif (entityType == "object"):
			return self.getObject(entityId)
			
		return None

	def deleteObject(self, objectId):
		for obj in self.objectList:
			if obj.id == objectId:
				self.objectList.remove(obj)

		for room in self.roomList:
			roomObject = room.getObject(objectId)
			if (roomObject):
				room.deleteObject(objectId)
				
	def addEnd(self, endObject, layerAttrs, endText, endImages):
		newView = View.End(self, endObject, layerAttrs, endText, endImages)
		self.endView = newView
		
	def addMenu(self, objectAttrs, layerAttrs, beginningImage, background, startButton, creditsButton, emptyButton):
		newView = View.Menu(self, objectAttrs, layerAttrs, beginningImage, background, startButton, creditsButton, emptyButton)
		
		self.menuView = newView
		
	def addSequence(self, layerAttrs, objectAttributes, imageAttributes):
		newView = View.Sequence(self, layerAttrs, objectAttributes, imageAttributes)
		self.sequenceList.append(newView)

	def addRoom(self, roomId, roomAttributes, roomImages):
		newView = View.Room(self, roomId, roomAttributes, roomImages)
		self.roomList.append(newView)

	# Create new generic object
	def addObject(self, room, objectAttributes, imageAttributes):
		newObject = Object.Object(self, room, objectAttributes, imageAttributes)
		self.__appendObject__(newObject, room)

	# JSON text object
	# TODO: What is the meaning of this?
	def addText(self, room, objectAttributes):
		newObject = Object.JSONText(self, room, objectAttributes)
		self.__appendObject__(newObject, room)

	# Create new item
	def addItem(self, room, objectAttributes, imageAttributes):
		newObject = Object.Item(self, room, objectAttributes, imageAttributes)
		self.__appendObject__(newObject, room)

	# Create new container
	def addContainer(self, room, objectAttributes, imageAttributes):
		newObject = Object.Container(self, room, objectAttributes, imageAttributes)
		self.__appendObject__(newObject, room)

	# Create new door
	def addDoor(self, room, objectAttributes, imageAttributes):
		newObject = Object.Door(self, room, objectAttributes, imageAttributes)	
		self.__appendObject__(newObject, room)

	# Create new obstacle
	def addObstacle(self, room, objectAttributes, imageAttributes):
		newObject = Object.Obstacle(self, room, objectAttributes, imageAttributes)
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
sc.saveScenario()

