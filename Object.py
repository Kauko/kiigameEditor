from random import randint

# Class for generic game objects and upper class for all the other objects
class Object(object):
	generalName = "Kiinteä esine"
	generalNameAdessive = "Kiinteällä esineellä"
	
	# Generic attributes for objects
	objectAttributes = {'object': {'music': ''}, 'className': 'Image'}
	
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
		if not (objectAttributes):
			objectAttributes = Object.objectAttributes
		if not (images):
			images = [JSONImage.imageAttributes]
			
		# Create image objects and objectId
		self.images = []

		if not (isinstance(self, JSONImage)):
			for image in images:
				self.images.append(JSONImage(texts, location, image, objectAttributes))
			if (objectId):
				self.id = Object.createUniqueId(objectId)
			else:
				self.id = Object.createUniqueId()
		# JSONImage doesn't need an image or an ID check
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
		except KeyError:
			return None	
			
	def setName(self, name):
		self.getRepresentingImage().texts["name"] = name
		
	def getPosition(self):
		return self.getRepresentingImage().getCoordinates()
		
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

	# Set item's examine (click) text
	def setExamineText(self, examineText):
		self.texts["examine"] = examineText
		
	# TODO: Should remove all texts referring to this object
	# Remove this object
	def remove(self):
		self.location.removeObject(self)
		
# Pickable item
class Item(Object):
	generalName = "Käyttöesine"
	generalNameAdessive = "Käyttöesineellä"
	
	# Generic attributes for items
	objectAttributes = {'className': 'Image', 'object': {'consume': False, 'category': 'item', 'outcome': '', 'trigger': ''}}
	
	def __init__(self, texts, location, itemId, images, objectAttributes):
		if not (objectAttributes):
			objectAttributes = Item.objectAttributes
		if not (images):
			images = [JSONImage.imageAttributes]
			
		super(Item, self).__init__(texts, location, itemId, images, objectAttributes)
		
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
		self.comesFrom = None
		self.trigger = None
		self.target = target
		self.outcome = None
		
	def setComesFrom(self, target):
		self.goesInto = None
		self.comesFrom = target
		self.trigger = None
		self.target = target
		self.outcome = None
		
	def clearTrigger(self):
		self.trigger = None
		self.target = None
		self.outcome = None
		
	def clearTarget(self):
		targetType = self.target.__class__.__name__
		if (targetType in ("Door", "Container")):
			self.target.setLocked(False)
		elif (targetType in ("Item", "Obstacle")):
			self.target.clearTrigger()
		
		self.trigger = None
		self.target = None
		self.goesInto = None
		self.comesFrom = None
		self.outcome = None
		
	# Set the item use text if target is defined
	def setUseText(self, useText):
		if (self.target):
			self.texts[self.target.id] = useText
			
	# Set item's pickup text
	def setPickupText(self, pickupText):
		self.texts["pickup"] = pickupText
		
	def setOutcome(self, outcomeObject):
		self.outcome = outcomeObject
		
	def setConsume(self, isConsumed):
		self.objectAttributes["object"]["consume"] = isConsumed
		
	def getConsume(self):
		return self.objectAttributes["object"]["consume"]
		
	# Get the text displayed when this item is used on its target
	def getUseText(self):
		useImage = self.target.getUseImage(self)
		try:
			return self.texts[useImage.id]
		except KeyError:
			self.texts[useImage.id] = ""
			return ""
			
	# Get the image activated by the given item
	def getUseImage(self, useItem):
		return self.images[0]
		
	# Set the object triggered by this item
	# objectRole=0 act as a key, =1 act as inItem, =2, act as outItem
	def setTargetObject(self, targetObject, objectRole=0):
		if not (targetObject):
			return
			
		triggerType = targetObject.__class__.__name__
		
		#self.clearTarget()
		self.target = targetObject
		
		if (triggerType in ("Object", "Item")):
			self.trigger = targetObject
			
		elif (triggerType in ("Door", "Container")):
			if (objectRole == 1):
				targetObject.setInItem(self)
				self.goesIn = targetObject
			elif (objectRole == 2):
				targetObject.setOutItem(self)
				self.comesFrom = targetObject
			else:
				targetObject.setKey(self)
				
		elif (triggerType == "Obstacle"):
			targetObject.setTrigger(self)
			
class Container(Object):
	generalName = "Säiliö"
	generalNameAdessive = "Säiliöllä"
	
	# Generic attributes for containers
	objectAttributes = {'className': 'Image', 'object': {'locked': False, 'full_image': '', 'state': 'empty', 'in': '', 'empty_image': '', 'out': '', 'category': 'container', 'blocked': False}}
	
	def __init__(self, texts, location, itemId, images, objectAttributes):
		if not (objectAttributes):
			objectAttributes = Container.objectAttributes
		if not (images):
			images = [JSONImage.imageAttributes]
			
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
			self.setKey(getGameObject("object", self.objectAttributes["object"]["key"]))

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

	# Returns True if container is locked, otherwise False
	def isLocked(self):
		try:
			if (self.objectAttributes["object"]["locked"] == True):
				return True
		except KeyError:
			print("Warning: Attribute 'locked' not defined for door object '%s'" %(self.id))
		return False

	def setIsLocked(self, isLocked):
		self.objectAttributes["object"]["locked"] = isLocked
		
	# Returns what unblocks the container
	def getKey(self):
		return self.key
		
	def setKey(self, keyObject):
		self.key = keyObject
		self.key.setTarget(self)
		
	def setInItem(self, inItemObject):
		# Clear old inItem
		if (self.inItem):
			self.inItem.clearTarget()
			
		# Set new inItem
		self.inItem = inItemObject
		if (self.inItem == self.key):
			self.key = None
		self.inItem.setGoesInto(self)
		
		# Set it to object's attributes
		self.objectAttributes["object"]["in"] = self.inItem.id
		
	def clearInItem(self):
		if (self.inItem):
			self.inItem.clearTarget()
		self.inItem = None
		
		try:
			del self.objectAttributes["object"]["in"]
		except KeyError:
			return
				
	def setOutItem(self, outItemObject):
		# Clear old outItem
		if (self.outItem):
			self.outItem.clearTarget()
			
		# Set new outItem
		self.outItem = outItemObject
		if (self.outItem == self.key):
			self.key = None
		self.outItem.setComesFrom(self)
		
		# Set it to object's attributes
		self.objectAttributes["object"]["out"] = self.outItem.id
		
	def clearOutItem(self):
		if (self.outItem):
			self.outItem.clearTarget()
		self.outItem = None
		
		try:
			del self.objectAttributes["object"]["out"]
		except KeyError:
			return
			
	# Set or remove locked state with images etc.
	# When setting locked=True, other parameters are mandatory
	def setLocked(self, setLocked, imagePath=None, keyObject=None):
		if (self.key):
			#self.key.clearTarget()
			self.key = None
			
		if (setLocked):
			imageObject = JSONImage(None, self.location, None, self.objectAttributes, imageId=self.id)
			if (imagePath):
				imageObject.setSource(imagePath)
			# TODO: Put other attributes here too	
			self.images.append(imageObject)
			self.lockedImage = imageObject
			
			self.objectAttributes["object"]["locked_image"] = imageObject.id
			
			self.setIsLocked(True)
			
			if (keyObject):
				self.key = keyObject
				self.key.setTarget(self)
				self.objectAttributes["object"]["key"] = keyObject.id
		else:
			try:
				del self.images[self.images.index(self.lockedImage)]
			except ValueError:
				pass
				
			try:
				self.objectAttributes["object"]["locked_image"]
			except KeyError:
				pass
				
			self.lockedImage = None
			self.setIsLocked(False)
			
	# Nullify current key
	def clearKey(self):
		if (self.key):
			self.key.clearTarget()
		self.key = None
		
class Door(Object):
	generalName = "Kulkureitti"
	generalNameAdessive = "Kulkureitillä"
	
	# Generic attributes for doors
	objectAttributes = {'className': 'Image', 'object': {'category': '', 'state': 'open', 'locked': False, 'transition': '', 'blocked': False, 'open_image': ''}}
	 
	def __init__(self, texts, location, itemId, images, objectAttributes):
		if not (objectAttributes):
			objectAttributes = Door.objectAttributes
		if not (images):
			images = [JSONImage.imageAttributes]
			
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
		try:
			self.blockedImage = self.getImage(objectAttributes["object"]["blocked_image"])
		except KeyError:
			self.blockedImage = None
		
		self.texts = {}
		
		try:
			if (self.closedImage):
				self.texts.update(texts[self.closedImage.id])
			
			if (self.lockedImage):
				self.texts.update(texts[self.lockedImage.id])
				
			if (self.openImage):
				self.texts.update(texts[self.openImage.id])
				
			if (self.blockedImage):
				self.texts.update(texts[self.blockedImage.id])
		except KeyError:
			print("Warning: Could not find texts.json entry for object '%s'" %(self.id))
			
		# Handle these in postInit
		self.key = None
		self.transition = None
		
	def postInit(self, getGameObject):
		try:
			self.setKey(getGameObject("object", self.objectAttributes["object"]["key"]))
		except KeyError:
			pass
			
		try:
			self.transition = getGameObject("room", self.objectAttributes["object"]["transition"])
		except KeyError:
			pass
		
	# Set or remove locked state with images etc.
	# When setting locked=True, other parameters can be given
	def setLocked(self, setLocked, imagePath=None, keyObject=None):
		if (self.key):
			#self.key.clearTarget()
			self.key = None
			
		if (setLocked):
			imageObject = JSONImage(None, self.location, None, self.objectAttributes, imageId=self.id)
			if (imagePath):
				imageObject.setSource(imagePath)
			# TODO: Put other attributes here too	
			self.images.append(imageObject)
			self.lockedImage = imageObject
			
			self.objectAttributes["object"]["locked_image"] = imageObject.id
			
			self.setIsLocked(True)
			
			if (keyObject):
				self.key = keyObject
				self.key.setTarget(self)
				self.objectAttributes["object"]["key"] = keyObject.id
		else:
			try:
				del self.images[self.images.index(self.lockedImage)]
			except ValueError:
				pass
				
			try:
				self.objectAttributes["object"]["locked_image"]
			except KeyError:
				pass
				
			self.lockedImage = None
			self.setIsLocked(False)
			
	def setClosed(self, setClosed):
		if (setClosed):
			imageObject = JSONImage(None, self.location, None, self.objectAttributes, imageId=self.id)
			self.images.append(imageObject)
			self.lockedImage = imageObject
			
			self.objectAttributes["object"]["closed_image"] = imageObject.id
		else:
			try:
				del self.images[self.images.index(self.closedImage)]
			except ValueError:
				pass
			
			try:
				del self.objectAttributes["object"]["closed_image"]
			except KeyError:
				pass
			self.closedImage = None
			
	def getImages(self):
		images = [self.closedImage, self.lockedImage, self.openImage, self.blockedImage]
		return list(filter((None).__ne__, images))
		
	def getRepresentingImage(self):
		return self.openImage

	# Get the image activated by the given item
	def getUseImage(self, useItem):
		if (self.key == useItem):
			return self.lockedImage
			
	def setTransition(self, roomObject):
		self.objectAttributes["object"]["transition"] = roomObject.id
		self.transition = roomObject
		
	# Returns True if door is locked, otherwise False
	def isLocked(self):
		try:
			if (self.objectAttributes["object"]["locked"] == True):
				return True
		except KeyError:
			print("Warning: Attribute 'locked' not defined for door object '%s'" %(self.id))
		return False

	def setIsLocked(self, isLocked):
		self.objectAttributes["object"]["locked"] = isLocked
		
	# Returns what unlocks the door
	#def getKey(self):
	#	return self.key
		
	def setKey(self, keyObject):
		self.key = keyObject
		self.key.setTarget(self)
		
	# Nullify current key
	def clearKey(self):
		if (self.key):
			self.key.clearTarget()
		self.key = None
		
class Obstacle(Object):
	generalName = "Este"
	generalNameAdessive = "Esteellä"
	
	# Generic attributes for obstacles
	objectAttributes = {'className': 'Image', 'object': {'related': [], 'target': '', 'trigger': '', 'blocking_image': '', 'category': 'obstacle', 'blocking': True}}
	
	def __init__(self, texts, location, itemId, images, objectAttributes):
		if not (objectAttributes):
			objectAttributes = Obstacle.objectAttributes
		if not (images):
			images = [JSONImage.imageAttributes]
			
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
		except KeyError:
			print("Warning: Could not find texts.json entry for object '%s'" %(self.id))
		try:
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
			self.setTrigger(getGameObject("object", self.objectAttributes["object"]["trigger"]))
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

	# Returns what unblocks the obstacle
	def getKey(self):
		return self.trigger
		
	# Set which object blocks
	def setTrigger(self, triggerObject):
		self.trigger = triggerObject
		self.trigger.setTarget(self)
		
	def clearTrigger(self):
		self.trigger.clearTarget()
		self.trigger = None
		
	def setBlockTarget(self, targetObject):
		self.blockTarget = targetObject
		self.objectAttributes["object"]["target"] = targetObject.id
		
	def clearBlockTarget(self):
		self.blockTarget = None
		try:
			del self.objectAttributes["object"]["target"]
		except KeyError:
			pass
				
# Image object representing what is in the JSON texts
class JSONImage(Object):
	imageAttributes = {'category': '', 'id': '', 'object_name': '', 'src': '', 'visible': False, 'x': 0, 'y': 0}
	
	# imageAttributes has to be dict, not a list as with other objects
	# objectAttributes is a dict with object, attrs and className keys
	def __init__(self, texts, location, imageAttributes, objectAttributes, imageId=None):
		if not (texts):
			texts = {}
	
		if not (imageAttributes):
			imageAttributes = JSONImage.imageAttributes
			
		if not (imageId):
			imageId = imageAttributes["id"]
			
		super(JSONImage, self).__init__(texts, location, imageId, None, objectAttributes)
		self.imageAttributes = imageAttributes
		
	def getRepresentingImage(self):
		return self
		
	def getSource(self):
		return self.imageAttributes["src"]
		
	def setSource(self, imagePath):
		# Cut the plain filename out of the name
		self.imageAttributes["src"] = "images/"+imagePath.split("/")[-1]
		
	def setObjectName(self, objectName):
		self.imageAttributes["object_name"] = objectName
		
	def setCoordinates(self, x, y):
		self.imageAttributes["x"] = x
		self.imageAttributes["y"] = y
		
	def getCoordinates(self):
		try:
			return (self.imageAttributes["x"], self.imageAttributes["y"])
		except KeyError:
			return
			
	def setCategory(self, category):
		self.imageAttributes["category"] = category
		
	def setObjectName(self, objectId):
		self.imageAttributes["id"] = objectId
		
# Differentiate sequence images from normal images
class SequenceImage(JSONImage):
	def __init__(self, texts, location, imageAttributes, objectAttributes, imageId=None):
		super(SequenceImage, self).__init__(texts, location, imageAttributes, objectAttributes, imageId)
		
	# Get the display time for this image
	def getShowTime(self):
		return self.location.getShowTime(self.id)
		
	# Get the fade type for this image
	def getDoFade(self):
		return self.location.getDoFade(self.id)
		
# Differentiate menu images from normal images
class MenuImage(JSONImage):
	def __init__(self, texts, location, imageAttributes, objectAttributes, imageId=None):
		super(MenuImage, self).__init__(texts, location, imageAttributes, objectAttributes, imageId)
		
