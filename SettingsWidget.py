from PySide import QtGui, QtCore
from ObjectImageSettings import ObjectImageSettings
from ImageCache import ImageCache

# TODO: On all comboboxes: What to do when item is in use? For example,
#		if an item is already a key to an object, how to display it?

# Item and room settings widget used in editor
class SettingsWidget(QtGui.QWidget):
	def __init__(self, parent=None):
		super(SettingsWidget, self).__init__(parent)
		
		self.currentObject = None
		self.lastObjectType = None
		self.useTypes = {0: "Ei käyttöä", 1: "Käytä toiseen esineeseen",
			2: "Avaa jotakin", 3: "Laita johonkin", 4: "Poista este"}
			
		self.layout = QtGui.QVBoxLayout()
		self.setLayout(self.layout)
		
		self.setSizePolicy(QtGui.QSizePolicy(
		QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed))
		
		self.parent = parent
		self.imageCache = ImageCache()
			
		self.createOtionFields()
		
	def displayOptions(self, gameObject):
		objectType = gameObject.__class__.__name__
		self.showWidgets(objectType)
		self.lastObjectType = objectType
		
		self.currentObject = gameObject
		
		if (objectType == "Room"):
			self.setRoomOptions(gameObject)
		elif (objectType == "Item"):
			self.setItemOptions(gameObject)
		elif (objectType == "Object"):
			self.setGenericOptions(gameObject)
		elif (objectType == "Door"):
			self.setDoorOptions(gameObject)
		elif (objectType == "Container"):
			self.setContainerOptions(gameObject)
		elif (objectType == "Obstacle"):
			self.setObstacleOptions(gameObject)
			
	def showWidgets(self, objectType):
		if (self.lastObjectType):
			for item in self.itemSettings[self.lastObjectType]:
				item.hide()
		for item in self.itemSettings[objectType]:
			item.show()
			
	# Settings for the object view
	def createOtionFields(self):
		# Name
		self.nameLabel = QtGui.QLabel("Nimi")
		self.objectNameEdit =  QtGui.QLineEdit()
		self.objectNameEdit.editingFinished.connect(self.changeName)
		
		# General image
		self.imgTextLabel = QtGui.QLabel("Kuva")
		self.objectImage = QtGui.QLabel(self)
		self.objectImage.mousePressEvent = lambda s: self.showImageDialog(self.changeObjectImage)
		
		self.useTextEdit = QtGui.QTextEdit()
		self.useTextEdit.setMaximumHeight(50)
		self.useTextEdit.focusOutEvent = lambda s: self.changeUseText()
		
		# Music
		# TODO: How to clear music?
		self.musicLabel = QtGui.QLabel("Musiikki")
		
		self.musicBtn = QtGui.QPushButton('Selaa...', self)
		self.musicBtn.setToolTip('Valitse musiikkitiedosto')
		self.musicBtn.resize(self.musicBtn.sizeHint())
		self.musicBtn.clicked.connect(lambda: self.showMusicDialog(self.changeMusic))
		
		self.musicTextEdit = QtGui.QLineEdit()
		self.musicTextEdit.setReadOnly(True)
		
		self.musicClear = QtGui.QPushButton('Ei musiikkia', self)
		self.musicClear.clicked.connect(self.clearMusic)
		
		# Where from dropdown box
		self.whereFromLabel = QtGui.QLabel("Mistä sinne pääsee?")
		
		# Where located
		self.whereLocatedLabel = QtGui.QLabel("Missä sijaitsee?")
		self.roomCombo = QtGui.QComboBox(self)
		self.roomCombo.setIconSize(QtCore.QSize(50,50))
		self.populateRoomCombobox(self.roomCombo)
		self.roomCombo.currentIndexChanged.connect(lambda: self.changeWhereLocated(self.roomCombo))
		
		# Where located combo with "No room" option
		self.roomComboItem = QtGui.QComboBox(self)
		self.roomComboItem.setIconSize(QtCore.QSize(50,50))
		self.roomComboItem.addItem("Ei sijaitse huoneessa")
		self.populateRoomCombobox(self.roomComboItem)
		self.roomComboItem.currentIndexChanged.connect(lambda: self.changeWhereLocated(self.roomComboItem))
		
		self.examineTextLabel = QtGui.QLabel("Teksti klikatessa:")
		self.examineTextEdit = QtGui.QTextEdit()
		self.examineTextEdit.setMaximumHeight(50)
		self.examineTextEdit.focusOutEvent = lambda s: self.changeExamineText()
		
		# Pickup text section
		self.pickupLabel = QtGui.QLabel("Poiminta")
		self.pickupLabelLine = self.createSeparator()
		self.pickupLabelLine.setFrameStyle(QtGui.QFrame.HLine | QtGui.QFrame.Raised)
		self.pickupTextLabel = QtGui.QLabel("Teksti poimittaessa:")
		
		self.pickupTextEdit = QtGui.QTextEdit()
		self.pickupTextEdit.setMaximumHeight(50)
		self.pickupTextEdit.focusOutEvent = lambda s: self.changePickupText()
		
		self.pickupBlockLabel = QtGui.QLabel("Estääkö jokin poiminnan?")
		self.pickupBlockCombo = self.createItemCombobox(None, ("obstacle",))
		
		# Object usage
		self.useLabel = QtGui.QLabel("Käyttö")
		self.useLabelLine = self.createSeparator()
		
		# Object type of usage
		self.useTypeCombo = QtGui.QComboBox(self)
		for i in self.useTypes:
			self.useTypeCombo.addItem(self.useTypes[i])
		self.useTypeCombo.currentIndexChanged.connect(self.changeUseType)
		
		self.useTextLabel = QtGui.QLabel("Teksti käytettäessä:")
		
		# Use target
		self.useTargetCombo = self.createItemCombobox("Ei mikään")
		self.useTargetCombo.currentIndexChanged.connect(self.changeUseTarget)
		
		self.allTextsButton = QtGui.QPushButton("Nämä ja muut tekstit")
		self.allTextsButton.clicked.connect(self.showAllTexts)
		
		# Door widgets
		self.doorTransitionLabel = QtGui.QLabel("Mihin ovesta pääsee?")
		self.doorTransitionCombo = QtGui.QComboBox(self)
		self.doorTransitionCombo.setIconSize(QtCore.QSize(50,50))
		self.populateRoomCombobox(self.doorTransitionCombo)
		self.doorTransitionLabelLine = self.createSeparator()
		
		self.openDoorImage = ObjectImageSettings("Avoin ovi", "Avoimen oven nimi", parent=self)
		self.closedDoorImage = ObjectImageSettings("Suljettu ovi", "Suljetun oven nimi", parent=self)
		self.lockedDoorImage = ObjectImageSettings("Lukittu ovi", "Lukitun oven nimi", True, "Onko ovi lukossa?", parent=self)
		
		# Container widgets
		self.lockedContainerImage = ObjectImageSettings("Lukittu säiliö", "Lukitun säiliön nimi", True, "Onko säiliö lukossa?", parent=self)
		self.fullContainerImage = ObjectImageSettings("Täysi säiliö", "Avoimen säiliön nimi", parent=self)
		self.emptyContainerImage = ObjectImageSettings("Tyhjä säiliö", "Tyhjän säiliön nimi", parent=self)
		
		# Obstacle widgets
		self.obstacleImage = ObjectImageSettings(None, "Esteen nimi", True, "Onko säiliö lukossa?", parent=self)
		self.obstacleBlocksLabel = QtGui.QLabel("Mitä estää?")
		self.obstacleBlocksCombo = self.createItemCombobox("Ei mitään", ("door",))
		
		self.whatGoesLabel = QtGui.QLabel("Mikä esine menee säiliöön?")
		self.whatGoesCombo = self.createItemCombobox("Ei mikään")
		
		self.whatComesLabel = QtGui.QLabel("Minkä esineen säiliöstä saa?")
		self.whatComesCombo = self.createItemCombobox("Ei mitään")
		
		self.layout.addWidget(self.nameLabel)
		self.layout.addWidget(self.objectNameEdit)
		self.layout.addWidget(self.imgTextLabel)
		self.layout.addWidget(self.objectImage)
		
		self.layout.addWidget(self.musicLabel)
		self.layout.addWidget(self.musicTextEdit)
		self.layout.addWidget(self.musicBtn)
		self.layout.addWidget(self.musicClear)
		self.layout.addWidget(self.whereFromLabel)
		self.layout.addWidget(self.whereLocatedLabel)
		self.layout.addWidget(self.roomCombo)
		self.layout.addWidget(self.roomComboItem)
		
		self.layout.addWidget(self.examineTextLabel)
		self.layout.addWidget(self.examineTextEdit)
		self.layout.addWidget(self.pickupLabelLine)
		self.layout.addWidget(self.pickupLabel)
		self.layout.addWidget(self.pickupTextLabel)
		self.layout.addWidget(self.pickupTextEdit)
		self.layout.addWidget(self.pickupBlockLabel)
		self.layout.addWidget(self.pickupBlockCombo)
		self.layout.addWidget(self.useLabelLine)
		self.layout.addWidget(self.useLabel)
		self.layout.addWidget(self.useTypeCombo)
		self.layout.addWidget(self.useTargetCombo)
		self.layout.addWidget(self.useTextLabel)
		self.layout.addWidget(self.useTextEdit)
		self.layout.addWidget(self.allTextsButton)
		
		# TODO: "Remove this image" button for door images?
		self.layout.addWidget(self.doorTransitionLabelLine)
		self.layout.addWidget(self.doorTransitionLabel)
		self.layout.addWidget(self.doorTransitionCombo)
		
		self.layout.addWidget(self.openDoorImage)
		self.layout.addWidget(self.closedDoorImage)
		self.layout.addWidget(self.lockedDoorImage)
		
		self.layout.addWidget(self.lockedContainerImage)
		self.layout.addWidget(self.fullContainerImage)
		self.layout.addWidget(self.emptyContainerImage)
		
		self.layout.addWidget(self.obstacleImage)
		self.layout.addWidget(self.obstacleBlocksLabel)
		self.layout.addWidget(self.obstacleBlocksCombo)
		
		self.layout.addWidget(self.whatGoesLabel)
		self.layout.addWidget(self.whatGoesCombo)
		self.layout.addWidget(self.whatComesLabel)
		self.layout.addWidget(self.whatComesCombo)
		
		# Which widgets are shown with each object
		self.itemSettings = {
			"Room": [
				self.imgTextLabel,
				self.objectImage,
				self.nameLabel,
				self.objectNameEdit,
				self.musicLabel,
				self.musicTextEdit,
				self.musicBtn,
				self.musicClear,
				self.whereFromLabel
				# TODO: doorCombo for "where from" values
			],
			"Item": [
				self.nameLabel,
				self.objectNameEdit,
				self.imgTextLabel,
				self.objectImage,
				self.examineTextLabel,
				self.examineTextEdit,
				self.pickupLabelLine,
				self.pickupLabel,
				self.pickupTextLabel,
				self.pickupTextEdit,
				self.useLabelLine,
				self.useLabel,
				self.useTypeCombo,
				self.useTargetCombo,
				self.useTextLabel,
				self.useTextEdit,
				self.allTextsButton,
				self.whereLocatedLabel,
				self.roomComboItem # TODO: Some better system to move items around
				# TODO: outcomeCombo for choosing trigger outcome
			],
			"Object": [
				self.nameLabel,
				self.objectNameEdit,
				self.imgTextLabel,
				self.objectImage,
				self.examineTextLabel,
				self.examineTextEdit,
				self.whereLocatedLabel,
				self.roomCombo
				# TODO: whoTriggers for displaying what object triggers
			],
			"Door": [
				self.whereLocatedLabel,
				self.roomCombo,
				
				self.doorTransitionLabelLine,
				self.doorTransitionLabel,
				self.doorTransitionCombo,
				
				self.openDoorImage,
				self.closedDoorImage,
				self.lockedDoorImage
				# TODO: obstacleCombo for "who blocks" values
			],
			"Container": [
				self.whereLocatedLabel,
				self.roomCombo,
				
				self.lockedContainerImage,
				self.fullContainerImage,
				self.emptyContainerImage,
				
				self.whatGoesLabel,
				self.whatGoesCombo,
				self.whatComesLabel,
				self.whatComesCombo
			],
			"Obstacle": [
				self.whereLocatedLabel,
				self.roomCombo,
				
				self.obstacleImage,
				self.obstacleBlocksLabel,
				self.obstacleBlocksCombo
			]
		}
		
		# Hide every widget
		for key in self.itemSettings:
			for item in self.itemSettings[key]:
				item.hide()
				
	# Set the input field values for rooms
	def setRoomOptions(self, room):
		# Room name
		self.setObjectName(room, "Huoneella")
		
		# Room background
		self.setobjectImage(self.parent.getImageDir()+"/"+room.getRepresentingImage().getSource())
		
		# Room music may return None which doesn't have split
		try:
			roomMusic = room.getMusic().split("/")[-1]
		except AttributeError:
			roomMusic = ""
		self.musicTextEdit.setText(roomMusic)
		
	# Set the input field values for items
	def setItemOptions(self, item):
		imageObject = item.getRepresentingImage()
		
		# Object name
		self.setObjectName(imageObject, "Esineellä")
		
		# Item image
		self.setobjectImage(self.parent.getImageDir()+"/"+imageObject.getSource())
		
		# Location
		self.setComboboxIndex(item.location, self.roomComboItem)
		
		# Examine text
		self.setExamineText()
		
		# Pickup text
		pickupText = item.getPickupText()
		if not (pickupText):
			pickupText = ""
		self.pickupTextEdit.setText(pickupText)
		
		# Set who blocks
		self.setComboboxIndex(item, self.pickupBlockCombo)
		
		# Use type of the item
		itemTarget = self.parent.getItemUse(item)
		
		itemTargetType = itemTarget.__class__.__name__
		useType = 0
		if (itemTargetType in ("Object", "Item")):
			useType = 1
		elif (itemTargetType == "Obstacle"):
			useType = 4
		elif (itemTargetType in ("Door", "Container")):
			# Item may unlock door or container or may go into a container
			if (itemTarget.key == item):
				useType = 2
			else:
				try:
					if (itemTarget.inItem == item):
						useType = 3
				except AttributeError:
					useType = 0
		self.setItemUse(useType, itemTarget)
		
		# Use text
		self.setUseText()
		
	# Set the input field values for generic objects
	def setGenericOptions(self, gObject):
		self.setObjectName(gObject, "Esineellä")
		
		imageObject = gObject.getRepresentingImage()
		self.setobjectImage(self.parent.getImageDir()+"/"+imageObject.getSource())
		
		# Location
		self.setComboboxIndex(gObject.location, self.roomCombo)
		
		# Examine text
		self.setExamineText()
			
	# Set the input field values for containers
	def setContainerOptions(self, container):
	
		# Set image settings for each image
		self.lockedContainerImage.setSettings(container, container.lockedImage)
		self.fullContainerImage.setSettings(container, container.fullImage)
		self.emptyContainerImage.setSettings(container, container.emptyImage)
		
		# Set location
		self.setComboboxIndex(container.location, self.roomCombo)
		
		# Set what goes, what comes from the container
		self.setComboboxIndex(container.inItem, self.whatGoesCombo)
		self.setComboboxIndex(container.outItem, self.whatComesCombo)
		
	# Set the input field values for obstacles
	def setObstacleOptions(self, obstacle):
	
		# Set image settings for each image
		self.obstacleImage.setSettings(obstacle, obstacle.blockingImage)
		
		# Set location
		self.setComboboxIndex(obstacle.location, self.roomCombo)
	
	def setobjectImage(self, imagePath, objectImage=None):
		imgPixmap = self.imageCache.createPixmap(imagePath)
		
		# TODO: Have spacing for smaller items
		if (imgPixmap.size().height() > 200):
			imgPixmap = imgPixmap.scaled(200, 200, QtCore.Qt.KeepAspectRatio)
			
		if (objectImage):
			objectImage.setPixmap(imgPixmap)
		else:
			self.objectImage.setPixmap(imgPixmap)
		
	# Set object use type
	def setItemUse(self, typeIndex, useItem):
		self.useTypeCombo.setCurrentIndex(typeIndex)
		
		# Find the combobox item with the given item
		for i in range(self.useTargetCombo.count()):
			if (self.useTargetCombo.itemData(i) == useItem):
				self.useTargetCombo.setCurrentIndex(i)
		
	# TODO: Door needs "who blocks" field?
	def setDoorOptions(self, doorObject):
		# Set each image's settings
		self.openDoorImage.setSettings(doorObject, doorObject.openImage)
		self.closedDoorImage.setSettings(doorObject, doorObject.closedImage)
		self.lockedDoorImage.setSettings(doorObject, doorObject.lockedImage)
		
		# Location
		self.setComboboxIndex(doorObject.location, self.roomCombo)
		
		# Door transition room
		self.setComboboxIndex(doorObject.transition, self.doorTransitionCombo)
		
	# Set use item for items
	def setUseText(self, textEdit=None, item=None):
		if not (item):
			item = self.currentObject

		useText = item.getUseText()
		if not (useText):
			useText = ""
			
		if (textEdit):
			textEdit.setText(useText)
		else:
			self.useTextEdit.setText(useText)
			
	# Set examine text for the given object
	def setExamineText(self, gameObject=None, textEdit=None):
		if not (gameObject):
			gameObject = self.currentObject
			
		try:
			text = gameObject.getExamineText()
		except AttributeError:
			text = ""
		
		if (textEdit):
			textEdit.setText(text)
		else:
			self.examineTextEdit.setText(text)
			
	# Set any game object name
	def setObjectName(self, gameObject, textStart, textEdit=None):
		# Given image may be None
		try:
			name = gameObject.getName()
		except AttributeError:
			name = ""
			
		if (name == None):
			name = "%s ei ole nimeä" %(textStart)
			
		# If textEdit is defined, set its text instead
		if (textEdit):
			textEdit.setText(name)
		else:
			self.objectNameEdit.setText(name)
		
	def changeWhereLocated(self, combobox):
		print("Change where located to",combobox.itemData(combobox.currentIndex()))
		
	# Text that comes after using an item
	def changeUseText(self):
		# TODO: Disable text field if no target is selected
		self.currentObject.setUseText(self.useTextEdit.toPlainText())
		
	def changePickupText(self):
		self.currentObject.setPickupText(self.pickupTextEdit.toPlainText())
		
	def changeExamineText(self):
		self.currentObject.setExamineText(self.examineTextEdit.toPlainText())
		
	# Change the image of a gameobject
	def changeObjectImage(self, imagePath, image=None):
		# If no image, a default image var will be used
		self.setobjectImage(imagePath, image)
		
		self.currentObject.getRepresentingImage().setImagePath(imagePath)
		
	# Change music
	def changeMusic(self, imagePath):
		self.currentObject.setMusic(imagePath)
		
	def changeName(self):
		# TODO: What if blank name?
		# TODO: Update whatever item listings displaying item's name (main tab, ...)
		self.currentObject.setName(self.objectNameEdit.text())
		
	# Change object use type
	def changeUseType(self, index):
		# TODO: Clear and disable useText field
		self.updateUseTargetCombobox(index, self.useTargetCombo)
		
	def changeCombobox(self, sourceValue, changeValue):
		print("change combo!", sourceValue, changeValue)
		
	# Set item use target
	def changeUseTarget(self, index):
		targetType = self.useTargetCombo.itemData(index).__class__.__name__
		if (targetType in ("Door", "Container")):
			if not (self.useTargetCombo.itemData(index).lockedImage):
				print("Target doesn't have locked image!")
				# TODO: What to do if target doesn't have locked image?
				return
				
		self.currentObject.setTargetObject(self.useTargetCombo.itemData(index))
		self.setUseText()
		
	def showAllTexts(self):
		print("Clicked show all texts")
		
	def clearMusic(self):
		print("Clear music clicked!")
		
	# Sets the index of a combobox according to given targetObject
	def setComboboxIndex(self, targetObject, combobox):
		# Find the combobox item with the given item
		for i in range(combobox.count()):
			if (combobox.itemData(i) == targetObject):
				combobox.setCurrentIndex(i)
				return
		combobox.setCurrentIndex(0)
		
	# Create combobox from given items with default of all item types
	def createItemCombobox(self, firstItem, objectTypes=None):
		if not (objectTypes):
			objectTypes = ("object", "item", "door", "container", "obstacle")
		
		combobox = QtGui.QComboBox(self)
		combobox.setIconSize(QtCore.QSize(50,50))
		
		self.populateCombobox(objectTypes, combobox, firstItem)
		return combobox
		
	# Populate a given combobox with game rooms
	def populateRoomCombobox(self, combobox):
		for room in self.parent.getRoomObjects():
			# TODO: Some model to eliminate redundancy from getName/roomName patterns
			roomName = room.getName()
			if not (roomName):
				roomName = "Huoneella ei ole nimeä"
			imgPixmap = self.imageCache.createPixmap(self.parent.getImageDir()+"/"+room.getRepresentingImage().getSource())
			
			roomIcon = QtGui.QIcon(imgPixmap)
			combobox.addItem(roomIcon, roomName, userData=room)
			
	# Create use target combobox
	def updateUseTargetCombobox(self, useType, combobox):
		if (useType == 0):
			objectTypes = ()
		elif (useType == 1):
			objectTypes = ("item", "object")
		elif (useType == 2):
			objectTypes = ("door", "container")
		elif (useType == 3):
			objectTypes = ("container",)
		else:
			objectTypes = ("obstacle",)
			
		self.populateCombobox(objectTypes, combobox, "Ei valittu")
		
	# TODO: Create a combo icon of multi-part objects such as cieni
	#		(those with "related" attribute)
	#def populateBlockingCombobox(self):
	#	self.populateCombobox(("obstacle",), self.pickupBlockCombo, "Ei estä")
		
	# Populate a given combobox with given types of objects
	# categorized by game rooms
	def populateCombobox(self, objectTypes, combobox, firstItem=None):
		# TODO: Disconnect combobox from events when populating it
		combobox.clear()
		
		itemCounter = 0
		
		# Add the given string as the first item
		if (firstItem):
			combobox.addItem(firstItem)
			itemCounter = 1
		
		for objType in objectTypes:
			objRooms = self.parent.getObjectsByType(objType)
			
			# Combobox has rooms with their obstacles under them
			for room in objRooms:
				roomObject = room["room"]
				roomName = roomObject.getName()
				if not (roomName):
					roomName = "Huoneella ei ole nimeä"
				imgPixmap = self.imageCache.createPixmap(self.parent.getImageDir()+"/"+roomObject.getRepresentingImage().getSource())
				
				roomIcon = QtGui.QIcon(imgPixmap)
				
				# Add room to the combobox and disallow choosing it
				combobox.addItem(roomIcon, roomName)
				combobox.setItemData(itemCounter, 0, QtCore.Qt.UserRole - 1);
				itemCounter += 1
				
				# TODO: Indendation of objects in the combobox
				# Add objects under the room
				for obj in room["objects"]:
					# Don't display the triggering item itself
					if (obj == self.currentObject):
						continue
					if (obj.getClassname() == "Text"):
						continue
					
					imageObject = obj.getRepresentingImage()
					imgPixmap = self.imageCache.createPixmap(self.parent.getImageDir()+"/"+imageObject.getSource())
					targetIcon = QtGui.QIcon(imgPixmap)
					combobox.addItem(targetIcon, imageObject.getName(), userData=obj)
					itemCounter += 1
					
	def showMusicDialog(self, callBack):
		fname, _ = QtGui.QFileDialog.getOpenFileName(self,
		'Valitse musiikkitiedosto','~', "Musiikkitiedostot (*.mp3 *.ogg)")
		# TODO: Modified object requires filename in format "audio/filename.xxx"
		if (len(fname) != 0):
			self.musicTextEdit.setText(fname.split("/")[-1])
			callBack(fname)
			
	def showImageDialog(self, callBack):
		fname, _ = QtGui.QFileDialog.getOpenFileName(self,
		'Valitse taustakuva','~', "Taustakuvat (*.png)")
		# TODO: Modified object requires filename in format "images/filename.png"
		
		if (len(fname) != 0):
			callBack(fname)
			
	def createSeparator(self):
		label = QtGui.QLabel("")
		label.setFrameStyle(QtGui.QFrame.HLine | QtGui.QFrame.Raised)
		return label
