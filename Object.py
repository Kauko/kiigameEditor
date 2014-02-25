# Class for generic objects and upper class for all the other objects
class Object(object):
	def __init__(self):
		self.id = ""
		self.name = ""
		self.image = ""
		self.examine = ""
		self.whatBlocks = None

# Pickable item
class Item(Object):
	def __init__(self):
		super(Item, self).__init__()
		self.pickUpText = ""
		self.interaction = None

class Container(Object):
	def __init__(self):
		super(Container, self).__init__()
		self.locked = False
		self.key = None
		self.inItem = None
		self.outItem = None

class Door(Object):
	def __init__(self):
		super(Door, self).__init__()
		self.closedImage = self.image
		self.lockedImage = ""
		self.openImage = ""
		self.locked = False
		self.key = None
		self.destination = None

class Obstacle(Object):
	def __init__(self):
		super(Obstacle, self).__init__()
		self.blockingImage = self.image
		self.unblockingImage = ""
		self.blockTarget = None
		self.trigger = None
