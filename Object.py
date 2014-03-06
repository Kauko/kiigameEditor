from random import randint

# Class for generic game objects and upper class for all the other objects
class Object(object):
	def __init__(self, data, location, objectAttributes, imageAttributes):
		# TODO: Check id collision, "running" id instead of randint?
		#		Static ID counter?
		if ("id" in objectAttributes):
			self.id = objectAttributes["id"]
		elif ("id" in imageAttributes[0]):
			self.id = imageAttributes[0]["id"]
		else:
			self.id = int(randint(0, 1000000000))
			
		#self.whatBlocks = None # TODO: In interaction instead?
		self.location = location
		self.objectAttributes = objectAttributes
		self.texts = data.getText(self.id)
		
		# JSONText and JSONImages don't need image
		if (imageAttributes):
			self.image = JSONImage(data, location, imageAttributes[0])
			
	# Return attributed object image (closed_image etc.) from imageAttributes
	def __getAttributeImage__(self, attribute, imageAttributes):
		if (attribute in self.objectAttributes):
			imageId = self.objectAttributes[attribute]
			for attr in imageAttributes:
				if (attr["id"] == imageId):
					return attr
		return None
		
	def postInit(self, getGameObject):
		return
		
	def getImages(self):
		images = [self.image]
		return list(filter((None).__ne__, images))
		
	
# Pickable item
class Item(Object):
	def __init__(self, data, room, objectAttributes, imageAttributes):
		super(Item, self).__init__(data, room, objectAttributes, imageAttributes)
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
	def __init__(self, data, room, objectAttributes, imageAttributes):
		super(Container, self).__init__(data, room, objectAttributes, imageAttributes)
		
		# Create the available door image objects
		self.emptyImage = None
		self.lockedImage = None
		self.fullImage = None
		emptyImage = self.__getAttributeImage__("empty_image", imageAttributes)
		lockedImage = self.__getAttributeImage__("locked_image", imageAttributes)
		fullImage = self.__getAttributeImage__("full_image", imageAttributes)
		
		if (emptyImage):
			self.emptyImage = JSONImage(data, self, emptyImage)
		if (lockedImage):
			self.lockedImage = JSONImage(data, self, lockedImage)
		if (fullImage):
			self.fullImage = JSONImage(data, self, fullImage)
		
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
	def __init__(self, data, room, objectAttributes, imageAttributes):
		super(Door, self).__init__(data, room, objectAttributes, imageAttributes)
		
		# Create the available door image objects
		self.closedImage = None
		self.lockedImage = None
		self.openImage = None
		closedImage = self.__getAttributeImage__("closed_image", imageAttributes)
		lockedImage = self.__getAttributeImage__("locked_image", imageAttributes)
		openImage = self.__getAttributeImage__("open_image", imageAttributes)
		
		if (closedImage):
			self.closedImage = JSONImage(data, self, closedImage)
		if (lockedImage):
			self.lockedImage = JSONImage(data, self, lockedImage)
		if (openImage):
			self.openImage = JSONImage(data, self, openImage)
		
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
	def __init__(self, data, room, objectAttributes, imageAttributes):
		super(Obstacle, self).__init__(data, room, objectAttributes, imageAttributes)
		
		# Create the available door image objects
		self.blockingImage = None
		self.unblockingImage = None
		blockingImage = self.__getAttributeImage__("blocking_image", imageAttributes)
		# TODO: Unblocking not implemented in kiigame
		unblockingImage = self.__getAttributeImage__("unblocking_image", imageAttributes)
		
		if (blockingImage):
			self.blockingImage = JSONImage(self, blockingImage)
		if (unblockingImage):
			self.unblockingImage = JSONImage(self, unblockingImage)
			
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
		
# Interaction data for pickable items
class Interaction(object):
	def __init__(self):
		self.parentItem = None
				
		self.comesFrom = None # Container
		
		# TODO: Implicit and explicit triggers are silly.
		#		Why couldn't the triggered item have the triggering item info
		# 		in implicit manner?
		
		self.triggerType = "" # goesInto/keyTo/triggerTo
		self.triggerTarget = None
		self.triggerOutcome = None # Only when triggerTo used
		
		self.interactionTexts = {} # From texts.json
		self.consume = False
		
		#self.setTriggerType(triggerType, triggerTarget)
		
	# Three kinds of item triggers
	# goesInto = item goes into a locker
	# keyTo = item opens locker or door
	# triggerTo = what item triggers
	def setTriggerType(self, triggerType, triggerTarget, triggerOutcome=None):
		if not (triggerType in ("goesInto", "keyTo", "triggerTo")):
			return
			
		# triggerTo requires outcome parameter
		if (triggerType == "triggerTo"):
			#if not (triggerOutcome):
			#	raise Exception("triggerTo requires triggerOutcome")
			#else:
			self.triggerOutcome = triggerOutcome
			
		# TODO: Check triggerTarget type?
		# TODO: When setting triggerTo, goesInto or keyTo
		#		the corresponding target item's attribute needs setting
		# 		(glue and poster for example)
		self.triggerTarget = triggerTarget
		
	def setText(self, objectId, text):
		if (not text or len(text) == 0):
			if (objectId in self.interactionTexts):
				self.interactionTexts.pop(objectId, None)
		else:
			self.interactionTexts[objectId] = text
			
	# If no default text in this item, use the master default value
	def setDefaultText(self, text):
		self.setText("default", text)
		
class JSONImage(Object):
	def __init__(self, data, location, imageAttributes):
		super(JSONImage, self).__init__(data, location, imageAttributes, None)
		
class JSONText(Object):
	def __init__(self, data, location, textAttributes):
		super(JSONText, self).__init__(data, location, textAttributes, None)
		
	def getImages(self):
		return [self]
		
