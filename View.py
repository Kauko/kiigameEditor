import Object
from random import randint

# Virtual class for views
class View(object):
	def __init__(self, id=None):
		# TODO: Check id collision, "running" id instead randint?
		#		Static ID counter?
		if not (id):
			self.id = int(randint(0, 1000000000))
		else:
			self.id = id
		#self.name = ""
		self.music = ""
		#self.type = "" # TODO: What was the idea of this again?

# Game cutscenes
class Sequence(View):
	def __init__(self, id=None):
		super(Sequence, self).__init__(id)
		self.images = []
		
	def deleteImage(self, imageId):
		for image in self.images:
			if (image.id == imageId):
				self.images.remove(image)

# Start menu
class Menu(View):
	def __init__(self, beginningImage, background, startButton, creditsButton, emptyButton):
		super(Menu, self).__init__("start")
		self.beginningImage = None
		self.background = None
		self.startButton = None
		self.creditsButton = None
		self.emptyButton = None

# End menu
class End(View):
	def __init__(self, endText, endImages):
		super(End, self).__init__("end")
		# TODO: End pictures are stupid
		# TODO: Before handling that, arrange pictures for UI?
		self.endImages = endImages
		self.endText = endText
		
	def deleteImage(self, imageId):
		for image in self.endImages:
			if (image.id == imageId):
				self.endImages.remove(image)

# Any game room
class Room(View):
	def __init__(self, id=None):
		super(Room, self).__init__(id)
		self.objectList = []
		self.background = None
		#self.comingFrom = []
		
	def deleteObject(self, objectId):
		for obj in self.objectList:
			if (obj.id == objectId):
				self.objectList.remove(obj)
