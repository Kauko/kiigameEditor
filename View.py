import Object
from random import randint

# Virtual class for views
class View(object):
	def __init__(self, viewAttributes, id=None):
		# TODO: Check id collision, "running" id instead randint?
		#		Static ID counter?
		if not (id):
			self.id = int(randint(0, 1000000000))
		else:
			self.id = id
		
		self.attrs = viewAttributes["attrs"]
		self.object = viewAttributes["object"]
		self.classname = viewAttributes["className"]
		
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
	def __init__(self, data, objectAttributes, layerAttrs, endText, endImages):
		super(End, self).__init__(layerAttrs, "end")
		
		self.endImages = []
		for image in endImages:
			self.endImages.append(Object.JSONImage(data, self, image))
			
		self.endText = Object.JSONText(data, self, endText)
		self.objectAttributes = objectAttributes
		
	def deleteImage(self, imageId):
		for image in self.endImages:
			if (image.id == imageId):
				self.endImages.remove(image)

# Any game room
class Room(View):
	def __init__(self, data, roomId, roomAttributes, roomImages):
		super(Room, self).__init__(roomAttributes, roomId)
		
		# Create objects inside the room
		self.objectList = []
		for imageId in roomImages:
			images = roomImages[imageId].pop("image")
			imageAttributes = roomImages[imageId]
			imageCategory = images[0]["category"]
			
			# Create objects according to the category
			if (imageCategory == "room_background"):
				self.background = Object.JSONImage(data, self, images[0])
			# TODO: Secret items - fix it in kiigame first
			elif (imageCategory == "item"):
				self.objectList.append(Object.Item(data, self, imageId, images, imageAttributes))
			elif (imageCategory == "container"):
				self.objectList.append(Object.Container(data, self, imageId, images, imageAttributes))
			elif (imageCategory == "door"):
				self.objectList.append(Object.Door(data, self, imageId, images, imageAttributes))
			elif (imageCategory == "obstacle"):
				self.objectList.append(Object.Obstacle(data, self, imageId, images, imageAttributes))
			else:
				self.objectList.append(Object.Object(data, self, imageId, images, imageAttributes))
				
	def deleteObject(self, objectId):
		for obj in self.objectList:
			if (obj.id == objectId):
				self.objectList.remove(obj)
				
