from random import randint

# Class for generic game objects and upper class for all the other objects
class Object(object):

	# Static method to create unique object ID
	usedIds = []
	def createUniqueId(newId=None):
		if not (newId):
			newId = str(randint(0, 1000000000))
			
		failed = False
		failCount = 0
		originalId = newId
		
		# Loop till unique ID found
		while (True):
			if not (newId in Object.usedIds):
				Object.usedIds.append(newId)
				return newId
			failCount += 1
			newId = "%s_%i" %(originalId, failCount)
			
	def __init__(self, data, location, objectId, images, objectAttributes):
		if (objectId):
			self.id = Object.createUniqueId(objectId)
		else:
			self.id = Object.createUniqueId()
			
		#self.whatBlocks = None # TODO: In interaction instead?
		self.location = location
		self.objectAttributes = objectAttributes
		self.texts = data.getText(self.id)
		
		# JSONImage doesn't need an image object
		self.images = []
		if not (isinstance(self, JSONImage)):
			for image in images:
				self.images.append(JSONImage(data, location, image, objectAttributes))
		
	# Return attributed object image (closed_image etc.) from imageAttributes
	def __getAttributeImage__(self, attribute, imageAttributes):
		if (attribute in self.objectAttributes):
			imageId = self.objectAttributes[attribute]
			for attr in imageAttributes:
				if (attr["id"] == imageId):
					return attr
		return None
		
	# Fill in attributes from objects that were missing during __init__
	def postInit(self, getGameObject):
		return
		
	def getImages(self):
		#images = [self.image]
		#return list(filter((None).__ne__, images))
		return self.images
		
	def getImage(self, imageId):
		for image in self.images:
			if (image.id == imageId):
				return image
		return None
		
	def getClassname(self):
		return self.objectAttributes["className"]
		
# Pickable item
class Item(Object):
	def __init__(self, data, location, itemId, images, objectAttributes):
		super(Item, self).__init__(data, location, itemId, images, objectAttributes)
		#self.interaction = interaction
		#self.interaction.parentItem = self
		
		# Handle these in postInit
		self.trigger = None
		self.outcome = None
		
	def postInit(self, getGameObject):
		try:
			self.trigger = getGameObject("object", self.objectAttributes["trigger"])
		except KeyError:
			pass
			
		try:
			self.outcome = getGameObject("object", self.objectAttributes["outcome"])
		except KeyError:
			pass
			
class Container(Object):
	def __init__(self, data, location, itemId, images, objectAttributes):
		super(Container, self).__init__(data, location, itemId, images, objectAttributes)
		
		# Create the available image objects
		try:
			self.emptyImage = self.getImage(objectAttributes["object"]["empty_image"])
		except KeyError:
			self.emptyImage = None
		try:
			self.lockedImage = self.getImage(objectAttributes["object"]["locked_image"])
		except KeyError:
			self.lockedImage = None
		try:
			self.fullImage = self.getImage(objectAttributes["object"]["full_image"])
		except KeyError:
			self.fullImage = None
			
		# Handle these in postInit
		self.key = None
		self.inItem = None
		self.outItem = None
		
	def postInit(self, getGameObject):
		try:
			self.key = getGameObject("object", self.objectAttributes["key"])
		except KeyError:
			pass
			
		try:
			self.inItem = getGameObject("object", self.objectAttributes["in"])
		except KeyError:
			pass
			
		try:
			self.outItem = getGameObject("object", self.objectAttributes["out"])
		except KeyError:
			pass
			
	def getImages(self):
		images = [self.emptyImage, self.lockedImage, self.fullImage]
		return list(filter((None).__ne__, images))
		
class Door(Object):
	def __init__(self, data, location, itemId, images, objectAttributes):
		super(Door, self).__init__(data, location, itemId, images, objectAttributes)
		
		# Create the available image objects
		try:
			self.emptyImage = self.getImage(objectAttributes["object"]["closed_image"])
		except KeyError:
			self.emptyImage = None
		try:
			self.lockedImage = self.getImage(objectAttributes["object"]["locked_image"])
		except KeyError:
			self.lockedImage = None
		try:
			self.fullImage = self.getImage(objectAttributes["object"]["open_image"])
		except KeyError:
			self.fullImage = None
			
		# Handle these in postInit
		self.key = None
		self.transition = None
		
	def postInit(self, getGameObject):
		try:
			self.key = getGameObject("object", self.objectAttributes["key"])
		except KeyError:
			pass
			
		try:
			self.transition = getGameObject("room", self.objectAttributes["transition"])
		except KeyError:
			pass
			
	def getImages(self):
		images = [self.closedImage, self.lockedImage, self.openImage]
		return list(filter((None).__ne__, images))
		
class Obstacle(Object):
	def __init__(self, data, location, itemId, images, objectAttributes):
		super(Obstacle, self).__init__(data, location, itemId, images, objectAttributes)
		# Create the available image objects
		try:
			self.blockingImage = self.getImage(objectAttributes["object"]["blocking_image"])
		except KeyError:
			self.blockingImage = None
		try:
			# TODO: To be implemented in kiigame
			self.unblockingImage = self.getImage(objectAttributes["object"]["unblocking_image"])
		except KeyError:
			self.unblockingImage = None
			
		# Handle these in postInit
		self.blockTarget = None
		self.trigger = None

	def postInit(self, getGameObject):
		try:
			self.blockTarget = getGameObject("object", self.objectAttributes["target"])
		except KeyError:
			pass
			
		try:
			self.trigger = getGameObject("object", self.objectAttributes["trigger"])
		except KeyError:
			pass
			
	def getImages(self):
		images = [self.blockingImage, self.unblockingImage]
		return list(filter((None).__ne__, images))
		
# Image object representing what is in the JSON data
class JSONImage(Object):
	# imageAttributes has to be dict, not a list as with other objects
	# objectAttributes is a dict with object, attrs and className keys
	def __init__(self, data, location, imageAttributes, objectAttributes):
		super(JSONImage, self).__init__(data, location, imageAttributes["id"], None, objectAttributes)
		self.imageAttributes = imageAttributes
		
