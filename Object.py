from random import randint

# Class for generic game objects and upper class for all the other objects
class Object(object):
	def __init__(self, id=None):
		# TODO: Check id collision, "running" id instead randint?
		#		Static ID counter?
		if not (id):
			self.id = int(randint(0, 1000000000))
		self.name = ""
		self.image = None
		self.examine = ""
		self.whatBlocks = None

# Pickable item
class Item(Object):
	def __init__(self, id=None):
		super(Item, self).__init__()
		self.pickUpText = ""
		self.interaction = None
		self.isSecret = False

class Container(Object):
	def __init__(self, id=None):
		super(Container, self).__init__()
		self.locked = False
		self.key = None
		self.inItem = None
		self.outItem = None
		
class Door(Object):
	def __init__(self, id=None):
		super(Door, self).__init__()
		self.closedImage = None
		self.lockedImage = None
		self.openImage = None
		self.locked = False
		self.key = None
		self.destination = None

class Obstacle(Object):
	def __init__(self, id=None):
		super(Obstacle, self).__init__()
		self.blockingImage = self.image
		self.unblockingImage = ""
		self.blockTarget = None
		self.trigger = None

# Objects derived from JSON
class JSONObject(object):
	def __init__(self, attributes, className="Image"):
		self.imageAttributes = attributes
		self.className = className

