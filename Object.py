from random import randint

# TODO: "None" attributes should be objects, not strings?

# Class for generic game objects and upper class for all the other objects
class Object(object):
	def __init__(self, objectAttributes, imageAttributes):
		# TODO: Check id collision, "running" id instead of randint?
		#		Static ID counter?
		#if not (id):
		#	self.id = int(randint(0, 1000000000))
		#else:
		#	self.id = id
		#self.name = ""
		#self.image = None
		#self.examine = ""
		#self.whatBlocks = None # TODO: In interaction instead?
		self.location = None
		self.image = JSONImage(imageAttributes)
		self.objectAttributes = objectAttributes

# Pickable item
class Item(Object):
	def __init__(self, objectAttributes, imageAttributes):
		super(Item, self).__init__(objectAttributes, imageAttributes)
		#self.pickUpText = ""
		#self.interaction = interaction
		#self.interaction.parentItem = self
		#self.isSecret = False
		
class Container(Object):
	def __init__(self, objectAttributes, imageAttributes):
		super(Container, self).__init__(objectAttributes, imageAttributes)
		#self.isLocked = False
		#self.key = None
		#self.inItem = None
		#self.outItem = None
		
class Door(Object):
	def __init__(self, objectAttributes, imageAttributes):
		super(Door, self).__init__(objectAttributes, imageAttributes)
		#self.closedImage = None
		#self.lockedImage = None
		#self.openImage = None
		#self.isLocked = False
		#self.key = None
		self.destination = None

class Obstacle(Object):
	def __init__(self, objectAttributes, imageAttributes):
		super(Obstacle, self).__init__(objectAttributes, imageAttributes)
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
		# TODO: What if no ID?
		#self.id = attributes["id"]
		#self.src = attributes["src"]
		
		# TODO: This is stupid
		#try:
		#	self.x = attributes["x"]
		#except KeyError:
		#	self.x = 0
			
		#try:
		#	self.y = attributes["y"]
		#except KeyError:
		#	self.y = 0

		self.objectAttributes = objectAttributes

class JSONText(object):
	def __init__(self, objectAttributes):
		# TODO: What if no ID?
		self.id = attributes["id"]
		self.objectAttributes = objectAttributes

class SequenceImage(object):
	def __init__(self, objectAttributese):
		# TODO: What if no ID?
		#self.id = id
		#self.src = src
		#self.doFade = doFade
		#self.showTime = showTime
		self.objectAttributes = objectAttributes
		
