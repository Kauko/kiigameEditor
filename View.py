import Object
from random import randint

# Virtual class for views
class View(object):

	# Static method to create unique view ID
	usedIds = []
	def createUniqueId(newId=None):
		if not (newId):
			newId = str(randint(0, 1000000000))
			
		failed = False
		failCount = 0
		originalId = newId
		
		# Loop till unique ID found
		while (True):
			if not (newId in View.usedIds):
				if (failed):
					print("Warning: Duplicate view ID '%s', new ID set as '%s'" %(originalId, newId))
				View.usedIds.append(newId)
				return newId
			failCount += 1
			failed = True
			newId = "%s_duplicate_%i" %(originalId, failCount)
			
	def __init__(self, texts, viewAttributes, viewId=None):
		if (viewId):
			self.id = View.createUniqueId(viewId)
		else:
			self.id = View.createUniqueId()
			
		self.attrs = viewAttributes["attrs"]
		self.object = viewAttributes["object"]
		self.classname = viewAttributes["className"]
		
		if (self.id in texts):
			self.texts = texts[self.id]
		else:
			self.texts = {}
		
	# Should be overriden by other view classes
	def getChildren(self):
		return
		
	# Should be overriden by other view classes
	def getItems(self):
		return
		
	# Should be overriden by other view classes
	def getItemById(self, itemId):
		return
		
	def getName(self):
		try:
			return self.texts["name"]
		except:
			return None
			
	def setName(self, name):
		self.texts["name"] = name
		
	def getMusic(self):
		try:
			return self.object["music"]
		except KeyError:
			return

	def setMusic(self, filePath):
		self.object["music"] = "audio/"+filePath.split("/")[-1]
		
	def clearMusic(self):
		del self.object["music"]

	# Post-init should be overriden by views
	def postInit(self, getGameObject):
		return
		
	# Remove given object
	# Should be overriden by other view classes
	def removeObject(self, childObject):
		return

class Menu(View):
	def __init__(self, texts, menuId, menuAttributes, menuImages):
		super(Menu, self).__init__(texts, menuAttributes, menuId)
		
		self.menuImages = []
		for imageId in menuImages:
			image = menuImages[imageId].pop("image")[0]
			imageAttributes = menuImages[imageId]
			menuImage = Object.MenuImage(texts, self, image, imageAttributes)
			self.menuImages.append(menuImage)
			
	def getItemById(self, itemId):
		for item in self.menuImages:
			if (item.id == itemId):
				return item

	def getChildren(self):
		return self.menuImages

# Game cutscenes
class Sequence(View):
	# Generic attributes for sequences
	sequenceAttributes = {'attrs': {'id': '', 'object_name': '', 'visible': False, 'category': 'sequence'}, 'object': {'music': '', 'images': {}, 'category': 'sequence'}, 'className': 'Layer'}
	
	def __init__(self, texts, sequenceId, sequenceAttributes, sequenceImages):
		if not (sequenceAttributes):
			sequenceAttributes = Sequence.sequenceAttributes
			
		super(Sequence, self).__init__(texts, sequenceAttributes, sequenceId)
		
		self.sequenceImages = []
		self.placeholderImage = None # If no other images, use this
		
		if not (sequenceImages):
			self.placeholderImage = Object.JSONImage(texts, self, None, None, self.id)
			self.placeholderImage.setSource("images/airfreshener.png")
			return
		
		# Create sequence image objects
		for image in sequenceImages:
			images = sequenceImages[image].pop("image")[0]
			imageAttributes = sequenceImages[image]
			sequenceImage = Object.SequenceImage(texts, self, images, imageAttributes)
			self.sequenceImages.append(sequenceImage)
			
	def deleteChild(self, imageId):
		for image in self.images:
			if (image.id == imageId):
				self.images.remove(image)
				
	def getChildren(self):
		return self.sequenceImages
		
	def getRepresentingImage(self):
		if (len(self.sequenceImages) == 0):
			return self.placeholderImage
		else:
			return self.sequenceImages[0]
			
		
	def getItems(self):
		return self.getChildren()
		
	# Get the display time for the given image
	def getShowTime(self, imageId):
		for i in self.object["images"]:
			if (self.object["images"][i]["id"] == imageId):
				return self.object["images"][i]["show_time"]
				
	# Set the display time for the given image
	def setShowTime(self, imageId, milliseconds):
		for i in self.object["images"]:
			if (self.object["images"][i]["id"] == imageId):
				self.object["images"][i]["show_time"] = milliseconds
				
	# Get the fade type for the given image
	def getDoFade(self, imageId):
		for i in self.object["images"]:
			if (self.object["images"][i]["id"] == imageId):
				return self.object["images"][i]["do_fade"]
				
	# Set the fade type for the given image
	def setDoFade(self, imageId, doFade):
		for i in self.object["images"]:
			if (self.object["images"][i]["id"] == imageId):
				self.object["images"][i]["do_fade"] = doFade
				
# Start menu
class Start(View):
	def __init__(self, texts, startAttributes, startImages):
		super(Start, self).__init__(texts, startAttributes, "start")
		
		for imageId in startImages:
			imageAttributes = startImages[imageId].pop("image")[0]
			objectAttributes = startImages[imageId]
			imageId = imageAttributes["id"]
			
			# Create objects according to its category
			if (imageId == "begining"):
				self.beginingImage = Object.JSONImage(texts, self, imageAttributes, objectAttributes)
			if (imageId == "start"):
				self.background = Object.JSONImage(texts, self, imageAttributes, objectAttributes)
			#if (imageId == "start_empty"):
			#	self.emptyButton = Object.JSONImage(texts, self, imageAttributes, objectAttributes)
				
	def postInit(self, getGameObject):
		# Create menu items
		menu = getGameObject("menu", self.object["menu"])
		for imageId,action in menu.object["items"].items():
			if (action == "start_game"):
				self.startButton = menu.getItemById(imageId)
			elif (action == "credits"):
				self.creditsButton = menu.getItemById(imageId)

	def getChildren(self):
		return [self.background, self.startButton, self.creditsButton, self.beginingImage]

	def getRepresentingImage(self):
		return self.background
		
	def getItems(self):
		return self.getChildren()
		
# End menu
class End(View):
	def __init__(self, texts, endAttributes, endImages):
		super(End, self).__init__(texts, endAttributes, "end")
		
		self.endImages = []
		for imageId in endImages:
			imageAttributes = endImages[imageId].pop("image")[0]
			objectAttributes = endImages[imageId]
			imageId = imageAttributes["id"]
			
			self.endImages.append(Object.JSONImage(texts, self, imageAttributes, objectAttributes))
			
	def postInit(self, getGameObject):
		# Create text item
		# TODO: Connect texts and ends in kiigame to get rid of hard coded ID
		self.endText = getGameObject("custom", "end_texts").getRepresentingImage()
		
	def deleteChild(self, imageId):
		for image in self.endImages:
			if (image.id == imageId):
				self.endImages.remove(image)

	def getChildren(self):
		return self.endImages
		
	def getItems(self):
		return self.endText,
		
	def getRepresentingImage(self):
		return self.endImages[0]
		
# Any game room
class Room(View):
	# Generic attributes for rooms
	roomAttributes = {'className': 'Layer', 'attrs': {'object_name': '', 'id': '', 'visible': False, 'category': 'room', 'start': False}, 'object': {'music': ''}}
	
	def __init__(self, texts, roomId, roomAttributes, roomImages):
		if not (roomAttributes):
			roomAttributes = Room.roomAttributes
			
		super(Room, self).__init__(texts, roomAttributes, roomId)
		
		self.objectList = []
		self.background = None
		self.placeholderImage = None
		
		if not (roomImages):
			self.placeholderImage = Object.JSONImage(texts, self, None, None, self.id)
			self.placeholderImage.setSource("images/airfreshener.png")
			return
			
		# Create objects inside the room including the background
		# TODO: Parsing objects could as well be done in View?
		self.background = None
		for imageId in roomImages:
			images = roomImages[imageId].pop("image")
			imageAttributes = roomImages[imageId]
			imageCategory = images[0]["category"]
			
			# Create objects according to their category
			if (imageAttributes["className"] == "Text"):
				self.objectList.append(Object.Text(texts, self, images, imageAttributes, imageId))
			elif (imageCategory == "room_background"):
				self.background = Object.JSONImage(texts, self, images[0], imageAttributes)
			# TODO: Secret items - fix it in kiigame first
			elif (imageCategory == "item"):
				self.objectList.append(Object.Item(texts, self, imageId, images, imageAttributes))
			elif (imageCategory == "container"):
				self.objectList.append(Object.Container(texts, self, imageId, images, imageAttributes))
			elif (imageCategory == "door"):
				self.objectList.append(Object.Door(texts, self, imageId, images, imageAttributes))
			elif (imageCategory == "obstacle"):
				self.objectList.append(Object.Obstacle(texts, self, imageId, images, imageAttributes))
			else:
				self.objectList.append(Object.Object(texts, self, imageId, images, imageAttributes))
				
	def deleteChild(self, objectId):
		for obj in self.objectList:
			if (obj.id == objectId):
				self.objectList.remove(obj)
	
	def getChildren(self):
		return [self.background] + self.objectList
	
	def getItems(self):
		return self.objectList
		
	def getRepresentingImage(self):
		if (self.background):
			return self.background
		else:
			return self.placeholderImage
			
	def postInit(self, getGameObject):
		for obj in self.objectList:
			obj.postInit(getGameObject)
			
	# Create new generic object
	def addObject(self, texts={}, objectAttributes=None, imageAttributes=None):
		imageId = self.id + "_object"
		newObject = Object.Object(texts, self, imageId, imageAttributes, objectAttributes)
		self.objectList.append(newObject)
		return newObject
		
	# Create new item
	def addItem(self, texts={}, objectAttributes=None, imageAttributes=None):
		imageId = self.id + "_item"
		newObject = Object.Item(texts, self, imageId, imageAttributes, objectAttributes)
		self.objectList.append(newObject)
		return newObject
		
	# Create new container
	def addContainer(self, texts={}, objectAttributes=None, imageAttributes=None):
		imageId = self.id + "_container"
		newObject = Object.Container(texts, self, imageId, imageAttributes, objectAttributes)
		self.objectList.append(newObject)
		return newObject
		
	# Create new door
	def addDoor(self, texts={}, objectAttributes=None, imageAttributes=None):
		imageId = self.id + "_door"
		newObject = Object.Door(texts, self, imageId, imageAttributes, objectAttributes)
		self.objectList.append(newObject)
		return newObject
		
	# Create new obstacle
	def addObstacle(self, texts={}, objectAttributes=None, imageAttributes=None):
		imageId = self.id + "_container"
		newObject = Object.Obstacle(texts, self, imageId, imageAttributes, objectAttributes)
		self.objectList.append(newObject)
		return newObject
		
	def removeObject(self, childObject):
		self.objectList.remove(childObject)
		
# Custom view for custom layers
class Custom(View):
	def __init__(self, texts, viewId, viewAttributes, viewImages):
		super(Custom, self).__init__(texts, viewAttributes, viewId)
		
		self.objectList = []
		for imageId in viewImages:
			images = viewImages[imageId].pop("image")
			imageAttributes = viewImages[imageId]
			
			print("attr", imageAttributes["className"], imageId)
			if (imageAttributes["className"] == "Text"):
				newObject = Object.Text(texts, self, images, imageAttributes, imageId)
			else:
				newObject = Object.Object(texts, self, imageId, images, imageAttributes)
			self.objectList.append(newObject)
				
	def deleteChild(self, objectId):
		for obj in self.objectList:
			if (obj.id == objectId):
				self.objectList.remove(obj)
	
	def getChildren(self):
		return self.objectList
		
	def getRepresentingImage(self):
		return self.objectList[0]#.getRepresentingImage()
		
	def getItems(self):
		print("JELLO")
		return self.objectList
