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
				if (failed):
					print("Warning: Duplicate object ID '%s', new ID set as '%s'" %(originalId, newId))
				Object.usedIds.append(newId)
				return newId
				
			failCount += 1
			failed = True
			newId = "%s_duplicate_%i" %(originalId, failCount)
			
	def __init__(self, texts, location, objectId, images, objectAttributes):
		# JSONImage doesn't need an image or an ID check
		self.images = []
		if not (isinstance(self, JSONImage)):
			for image in images:
				self.images.append(JSONImage(texts, location, image, objectAttributes))
			if (objectId):
				self.id = Object.createUniqueId(objectId)
			else:
				self.id = Object.createUniqueId()
		else:
			self.id = objectId
		
		#self.whatBlocks = None # TODO: In interaction instead?
		self.location = location
		self.objectAttributes = objectAttributes
		try:
			self.texts = texts[self.id]
		except KeyError:
			self.texts = {}
			print("Warning: Could not find texts.json entry for object '%s'" %(self.id))
		
	# Return attributed object image (closed_image etc.) from imageAttributes
	#def __getAttributeImage__(self, attribute, imageAttributes):
	#	if (attribute in self.objectAttributes):
	#		imageId = self.objectAttributes[attribute]
	#		for attr in imageAttributes:
	#			if (attr["id"] == imageId):
	#				return attr
	#	return None
		
	# Fill in attributes from objects that were missing during __init__
	# Every item needs to implement this
	def postInit(self, getGameObject):
		return
		
	def getImages(self):
		return self.images
		
	def getImage(self, imageId):
		for image in self.images:
			if (image.id == imageId):
				return image
		return None
		
	def getClassname(self):
		return self.objectAttributes["className"]
		
	def getName(self):
		try:
			return self.texts["name"]
		except:
			return None
		
	# Returns of the most "representing" image for an item such as open door
	# instead closed door image
	# Every item needs to override this to act properly
	def getRepresentingImage(self):
		return self.images[0]

	# Get the image activated by the given item
	# Should be overriden by other objects
	def getUseImage(self, useItem):
		return self.images[0]
		
	def getExamineText(self):
		try:
			return self.texts["examine"]
		except:
			return

# Pickable item
class Item(Object):
	def __init__(self, texts, location, itemId, images, objectAttributes):
		super(Item, self).__init__(texts, location, itemId, images, objectAttributes)
		#self.interaction = interaction
		#self.interaction.parentItem = self
		
		# Handle these in postInit
		self.trigger = None # Use on object
		self.outcome = None
		
		self.target = None # Can be any other object
		self.goesInto = None
		self.comesFrom = None
		
	def postInit(self, getGameObject):
		try:
			self.trigger = getGameObject("object", self.objectAttributes["object"]["trigger"])
			self.target = self.trigger
		except KeyError:
			pass
			
		try:
			self.outcome = getGameObject("object", self.objectAttributes["object"]["outcome"])
		except KeyError:
			pass
			
	def getPickupText(self):
		try:
			return self.texts["pickup"]
		except:
			return

	def getUse(self):
		if (self.target):
			return self.target
		elif (self.goesInto):
			return self.goesInto
		elif (self.comesFrom):
			return self.comesFrom
			
	def setTarget(self, target):
		self.target = target
		
	def setGoesInto(self, target):
		self.goesInto = target
		self.target = target
		
	def setComesFrom(self, target):
		self.comesFrom = target
		#self.target = target
		
	# Get the text displayed when this item is used on its target
	def getUseText(self):
		useImage = self.target.getUseImage(self)
		return self.texts[useImage.id]
		
	# Get the image activated by the given item
	def getUseImage(self, useItem):
		return self.images[0]

class Container(Object):
	def __init__(self, texts, location, itemId, images, objectAttributes):
		super(Container, self).__init__(texts, location, itemId, images, objectAttributes)
		
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
			
		self.texts = {}
		
		try:
			if (self.emptyImage):
				self.texts.update(texts[self.emptyImage.id])
			
			if (self.lockedImage):
				self.texts.update(texts[self.lockedImage.id])
				
			if (self.fullImage):
				self.texts.update(texts[self.fullImage.id])
		except KeyError:
			print("Warning: Could not find texts.json entry for object '%s'" %(self.id))
			
		# Handle these in postInit
		self.key = None
		self.inItem = None
		self.outItem = None
		
	def postInit(self, getGameObject):
		try:
			self.key = getGameObject("object", self.objectAttributes["object"]["key"])
			self.key.setTarget(self)
		except KeyError:
			pass

		try:
			self.inItem = getGameObject("object", self.objectAttributes["object"]["in"])
			self.inItem.setGoesInto(self)
		except KeyError:
			pass
			
		try:
			self.outItem = getGameObject("object", self.objectAttributes["object"]["out"])
			self.outItem.setComesFrom(self)
		except KeyError:
			pass
			
	def getImages(self):
		images = [self.emptyImage, self.lockedImage, self.fullImage]
		return list(filter((None).__ne__, images))
		
	def getRepresentingImage(self):
		return self.emptyImage

	# Get the image activated by the given item
	def getUseImage(self, useItem):
		if (self.key == useItem):
			return self.lockedImage
		elif (self.inItem == useItem):
			return self.emptyImage
		elif (self.outItem == useItem):
			return self.fullImage

class Door(Object):
	def __init__(self, texts, location, itemId, images, objectAttributes):
		super(Door, self).__init__(texts, location, itemId, images, objectAttributes)
		
		# Create the available image objects
		try:
			self.closedImage = self.getImage(objectAttributes["object"]["closed_image"])
		except KeyError:
			self.closedImage = None
		try:
			self.lockedImage = self.getImage(objectAttributes["object"]["locked_image"])
		except KeyError:
			self.lockedImage = None
		try:
			self.openImage = self.getImage(objectAttributes["object"]["open_image"])
		except KeyError:
			self.openImage = None
		
		self.texts = {}
		
		try:
			if (self.closedImage):
				self.texts.update(texts[self.closedImage.id])
			
			if (self.lockedImage):
				self.texts.update(texts[self.lockedImage.id])
				
			if (self.openImage):
				self.texts.update(texts[self.openImage.id])
		except KeyError:
			print("Warning: Could not find texts.json entry for object '%s'" %(self.id))
			
		# Handle these in postInit
		self.key = None
		self.transition = None
		
	def postInit(self, getGameObject):
		try:
			self.key = getGameObject("object", self.objectAttributes["object"]["key"])
			self.key.setTarget(self)
		except KeyError:
			pass
			
		try:
			self.transition = getGameObject("room", self.objectAttributes["object"]["transition"])
		except KeyError:
			pass
			
	def getImages(self):
		images = [self.closedImage, self.lockedImage, self.openImage]
		return list(filter((None).__ne__, images))
		
	def getRepresentingImage(self):
		return self.openImage

	# Get the image activated by the given item
	def getUseImage(self, useItem):
		if (self.key == useItem):
			return self.lockedImage

class Obstacle(Object):
	def __init__(self, texts, location, itemId, images, objectAttributes):
		super(Obstacle, self).__init__(texts, location, itemId, images, objectAttributes)
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
		
		self.texts = {}

		try:
			if (self.blockingImage):
				self.texts.update(texts[self.blockingImage.id])
			
			if (self.unblockingImage):
				self.texts.update(texts[self.unblockingText.id])
		except KeyError:
			print("Warning: Could not find texts.json entry for object '%s'" %(self.id))
			
		# Handle these in postInit
		self.blockTarget = None
		self.trigger = None

	def postInit(self, getGameObject):
		try:
			self.blockTarget = getGameObject("object", self.objectAttributes["object"]["target"])
		except KeyError:
			pass
			
		try:
			self.trigger = getGameObject("object", self.objectAttributes["object"]["trigger"])
			self.trigger.setTarget(self)
		except KeyError:
			pass
			
	def getImages(self):
		images = [self.blockingImage, self.unblockingImage]
		return list(filter((None).__ne__, images))
		
	def getRepresentingImage(self):
		return self.blockingImage

	# Get the image activated by the given item
	def getUseImage(self, useItem):
		if (self.trigger == useItem):
			return self.blockingImage

# Image object representing what is in the JSON texts
class JSONImage(Object):
	# imageAttributes has to be dict, not a list as with other objects
	# objectAttributes is a dict with object, attrs and className keys
	def __init__(self, texts, location, imageAttributes, objectAttributes):
		super(JSONImage, self).__init__(texts, location, imageAttributes["id"], None, objectAttributes)
		self.imageAttributes = imageAttributes
		
	def getLocation(self):
		return self.imageAttributes["src"]
		
	#def getUseText(self):
	#	try:
	#		return self.texts[self.target.id]
	#	except:
	#		return
