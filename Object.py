from random import randint

# Class for generic game objects and upper class for all the other objects
class Object(object):
	def __init__(self, room, objectAttributes, imageAttributes):
		# TODO: Check id collision, "running" id instead of randint?
		#		Static ID counter?
		if ("id" in objectAttributes):
			self.id = objectAttributes["id"]
		else:
			self.id = int(randint(0, 1000000000))
			
		#self.whatBlocks = None # TODO: In interaction instead?
		self.location = room
		self.image = JSONImage(imageAttributes)
		self.objectAttributes = objectAttributes

	# Set attributes that are available only after all objects are created
	def postInit(self, seekFunction):
		seekFunction("hello world :DDD")
		pass

# Pickable item
class Item(Object):
	def __init__(self, room, objectAttributes, imageAttributes):
		super(Item, self).__init__(room, objectAttributes, imageAttributes)
		#self.interaction = interaction
		#self.interaction.parentItem = self
		
class Container(Object):
	def __init__(self, room, objectAttributes, imageAttributes):
		super(Container, self).__init__(room, objectAttributes, imageAttributes)
		#self.isLocked = False
		#self.key = None
		#self.inItem = None
		#self.outItem = None
		
class Door(Object):
	def __init__(self, room, objectAttributes, imageAttributes):
		super(Door, self).__init__(room, objectAttributes, imageAttributes)
		
		# Create the available door image objects
		self.closedImage = None
		self.lockedImage = None
		self.openImage = None
		closedImage = self.__getAttributeImage__("closed_image", imageAttributes)
		lockedImage = self.__getAttributeImage__("locked_image", imageAttributes)
		openImage = self.__getAttributeImage__("open_image", imageAttributes)
		
		if (closedImage):
			self.closedImage = JSONImage(closedImage)
		if (lockedImage):
			self.lockedImage = JSONImage(lockedImage)
		if (openImage):
			self.openImage = JSONImage(openImage)
		
		# Handle these in postInit
		self.key = None
		self.destination = None
		
	# Get attributed door image (closed_image etc.) from imageAttributes
	# and create image object from it
	def __getAttributeImage__(self, attribute, imageAttributes):
		if (attribute in self.objectAttributes):
			imageId = self.objectAttributes[attribute]
			for attr in imageAttributes:
				if (attr["id"] == imageId):
					return attr
		return None
					
class Obstacle(Object):
	def __init__(self, room, objectAttributes, imageAttributes):
		super(Obstacle, self).__init__(room, objectAttributes, imageAttributes)
		#self.blockingImage = self.image
		#self.unblockingImage = None
		#self.blockTarget = ""
		#self.trigger = ""

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
		
class JSONImage(object):
	def __init__(self, objectAttributes):
		if ("id" in objectAttributes):
			self.id = objectAttributes["id"]
		else:
			self.id = int(randint(0, 1000000000))

		self.objectAttributes = objectAttributes

class JSONText(object):
	def __init__(self, objectAttributes):
		if ("id" in objectAttributes):
			self.id = objectAttributes["id"]
		else:
			self.id = int(randint(0, 1000000000))
			
		self.objectAttributes = objectAttributes
		
		
