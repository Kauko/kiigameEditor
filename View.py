import Object
from random import randint

# Virtual class for views
class View(object):
	def __init__(self, layerAttrs, id=None):
		# TODO: Check id collision, "running" id instead randint?
		#		Static ID counter?
		if not (id):
			self.id = int(randint(0, 1000000000))
		else:
			self.id = id
		
		# TODO: layerAttrs already includes id	
		self.layerAttrs = layerAttrs

# Game cutscenes
class Sequence(View):
	def __init__(self, data, layerAttrs, objectAttributes, imageAttributes):
		super(Sequence, self).__init__(layerAttrs, objectAttributes["id"])
		self.images = []
		
		self.objectAttributes = objectAttributes
		
		# Create image objects
		for image in imageAttributes:
			sequenceImage = Object.JSONImage(data, self, image)
			self.images.append(sequenceImage)
		
	def deleteImage(self, imageId):
		for image in self.images:
			if (image.id == imageId):
				self.images.remove(image)
				
# Start menu
class Menu(View):
	def __init__(self, data, objectAttributes, layerAttrs, beginingImage, background, startButton, creditsButton, emptyButton):
		super(Menu, self).__init__(layerAttrs, "start")
		
		self.objectAttributes = objectAttributes
		self.beginingImage = Object.JSONImage(data, self, beginingImage)
		self.background = Object.JSONImage(data, self, background)
		self.startButton = Object.JSONImage(data, self, startButton)
		self.creditsButton = Object.JSONImage(data, self, creditsButton)
		self.emptyButton = Object.JSONImage(data, self, emptyButton)

# End menu
class End(View):
	def __init__(self, data, layerAttrs, endText, endImages):
		super(End, self).__init__(layerAttrs, "end")
		
		self.endImages = []
		for image in endImages:
			self.endImages.append(Object.JSONImage(data, self, image))
			
		self.endText = Object.JSONText(data, self, endText)
		
	def deleteImage(self, imageId):
		for image in self.endImages:
			if (image.id == imageId):
				self.endImages.remove(image)

# Any game room
class Room(View):
	def __init__(self, data, viewAttributes, imageAttributes):
		super(Room, self).__init__(None, imageAttributes["id"])
		
		self.objectList = []
		self.background = Object.JSONImage(data, self, imageAttributes)
		self.layerAttrs = None # Hopefully set later
		self.viewAttributes = viewAttributes
	
	def getImage(self):
		image = self.background
		return image
		
	def deleteObject(self, objectId):
		for obj in self.objectList:
			if (obj.id == objectId):
				self.objectList.remove(obj)
				
