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
		
	def getChildren(self):
		return
		
	def getName(self):
		try:
			return self.texts["name"]
		except:
			return None
			
# Game cutscenes
class Sequence(View):
	def __init__(self, texts, sequenceId, sequenceAttributes, sequenceImages):
		super(Sequence, self).__init__(texts, sequenceAttributes, sequenceId)
		
		# Create sequence image objects
		self.sequenceImages = []
		for image in sequenceImages:
			images = sequenceImages[image].pop("image")[0]
			imageAttributes = sequenceImages[image]
			sequenceImage = Object.JSONImage(texts, self, images, imageAttributes)
			self.sequenceImages.append(sequenceImage)
			
	def deleteChild(self, imageId):
		for image in self.images:
			if (image.id == imageId):
				self.images.remove(image)
				
	def getChildren(self):
		return self.sequenceImages
		
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
			if (imageId == "start_game"):
				self.startButton = Object.JSONImage(texts, self, imageAttributes, objectAttributes)
			if (imageId == "start_credits"):
				self.creditsButton = Object.JSONImage(texts, self, imageAttributes, objectAttributes)
			if (imageId == "start_empty"):
				self.emptyButton = Object.JSONImage(texts, self, imageAttributes, objectAttributes)
				
	def getChildren(self):
		return [self.background, self.startButton, self.creditsButton, self.emptyButton, self.beginingImage]
		
# End menu
class End(View):
	def __init__(self, texts, endAttributes, endImages):
		super(End, self).__init__(texts, endAttributes, "end")
		
		self.endImages = []
		for imageId in endImages:
			imageAttributes = endImages[imageId].pop("image")[0]
			objectAttributes = endImages[imageId]
			imageId = imageAttributes["id"]
			
			# Create objects according to its category
			if (imageId == "rewards_text"):
				self.endText = Object.JSONImage(texts, self, imageAttributes, objectAttributes)
			else:
				self.endImages.append(Object.JSONImage(texts, self, imageAttributes, objectAttributes))
				
	def deleteChild(self, imageId):
		for image in self.endImages:
			if (image.id == imageId):
				self.endImages.remove(image)

	def getChildren(self):
		return self.endImages + [self.endText]
		
# Any game room
class Room(View):
	def __init__(self, texts, roomId, roomAttributes, roomImages):
		super(Room, self).__init__(texts, roomAttributes, roomId)
		
		# Create objects inside the room including the background
		# TODO: This could be done in super
		self.objectList = []
		for imageId in roomImages:
			images = roomImages[imageId].pop("image")
			imageAttributes = roomImages[imageId]
			imageCategory = images[0]["category"]
			
			# Create objects according to its category
			if (imageCategory == "room_background"):
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
	
	def getBackground(self):
		return self.background
		
	# TODO: These addX methods
	# Create new generic object
	def addObject(self, objectAttributes, imageAttributes):
		self.objectList.append(Object.Object(texts, self, imageId, images, imageAttributes))

	# Create new item
	def addItem(self, objectAttributes, imageAttributes):
		self.objectList.append(Object.Item(texts, self, imageId, images, imageAttributes))

	# Create new container
	def addContainer(self, objectAttributes, imageAttributes):
		self.objectList.append(Object.Container(texts, self, imageId, images, imageAttributes))

	# Create new door
	def addDoor(self, objectAttributes, imageAttributes):
		self.objectList.append(Object.Door(texts, self, imageId, images, imageAttributes))

	# Create new obstacle
	def addObstacle(self, objectAttributes, imageAttributes):
		self.objectList.append(Object.Obstacle(texts, self, imageId, images, imageAttributes))

	

# Custom view for custom layers
class Custom(View):
	def __init__(self, texts, viewId, viewAttributes, viewImages):
		super(Custom, self).__init__(texts, viewAttributes, viewId)
		
		# Create objects inside the room including the background
		self.objectList = []
		for imageId in viewImages:
			images = viewImages[imageId].pop("image")
			imageAttributes = viewImages[imageId]
			
			self.objectList.append(Object.Object(texts, self, imageId, images, imageAttributes))
				
	def deleteChild(self, objectId):
		for obj in self.objectList:
			if (obj.id == objectId):
				self.objectList.remove(obj)
	
	def getChildren(self):
		return self.objectList
		
