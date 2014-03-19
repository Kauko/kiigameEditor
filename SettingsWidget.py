from PySide import QtGui, QtCore
from ObjectImageSettings import ObjectImageSettings

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
		
		self.createItemOptions()
		#self.createRoomOptions()
		
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
	def createItemOptions(self):
		self.nameLabel = QtGui.QLabel("Nimi")
		
		self.musicTextEdit = QtGui.QLineEdit()
		self.musicTextEdit.setReadOnly(True)
		
		self.objectNameEdit =  QtGui.QLineEdit()
		
		self.itemImage = QtGui.QLabel(self)
		self.itemImage.mousePressEvent = lambda s: self.showImageDialog(self.setRoomBackground)
		
		self.useTypeCombo = QtGui.QComboBox(self)
		
		# TODO: This combobox should be taller with the item chosen
		self.useTargetCombo = QtGui.QComboBox(self)
		self.useTargetCombo.setIconSize(QtCore.QSize(50,50))
		self.useTargetCombo.currentIndexChanged.connect(self.setUseTarget)
		
		self.useTextEdit = QtGui.QTextEdit()
		self.useTextEdit.setMaximumHeight(50)
		
		# Music
		# TODO: How to clear music?
		self.musicLabel = QtGui.QLabel("Musiikki")
		self.musicBtn = QtGui.QPushButton('Selaa...', self)
		self.musicBtn.setToolTip('Valitse musiikkitiedosto')
		self.musicBtn.resize(self.musicBtn.sizeHint())
		self.musicBtn.clicked.connect(self.showMusicDialog)
		
		# Where from dropdown box
		self.whereFromLabel = QtGui.QLabel("Mistä sinne pääsee?")
		
		# Where located
		self.whereLocatedLabel = QtGui.QLabel("Missä sijaitsee?")
		self.roomCombo = QtGui.QComboBox(self)
		self.roomCombo.setIconSize(QtCore.QSize(50,50))
		self.populateRoomCombobox(self.roomCombo)
		
		# Where located combo with "No room" option
		self.roomComboItem = QtGui.QComboBox(self)
		self.roomComboItem.setIconSize(QtCore.QSize(50,50))
		self.roomComboItem.addItem("Ei sijaitse huoneessa")
		self.populateRoomCombobox(self.roomComboItem)
		
		# Object image
		self.imgTextLabel = QtGui.QLabel("Kuva")
		
		self.clickTextLabel = QtGui.QLabel("Teksti klikatessa:")
		
		self.clickTextEdit = QtGui.QTextEdit()
		self.clickTextEdit.setMaximumHeight(50)
		
		# Pickup text section
		self.pickupLabel = QtGui.QLabel("Poiminta")
		self.pickupLabelLine = self.createSeparator()
		self.pickupLabelLine.setFrameStyle(QtGui.QFrame.HLine | QtGui.QFrame.Raised)
		
		self.pickupTextLabel = QtGui.QLabel("Teksti poimittaessa:")
		
		self.pickupTextEdit = QtGui.QTextEdit()
		self.pickupTextEdit.setMaximumHeight(50)
		
		self.pickupBlockLabel = QtGui.QLabel("Estääkö jokin poiminnan?")
		
		self.pickupBlockCombo = QtGui.QComboBox(self)
		self.pickupBlockCombo.setIconSize(QtCore.QSize(50,50))
		self.populateBlockingCombobox()
		
		# Object usage
		self.useLabel = QtGui.QLabel("Käyttö")
		self.useLabelLine = self.createSeparator()
		#self.createSeparator(self.useLabelLine)
		#self.useLabelLine.setFrameStyle(QtGui.QFrame.HLine | QtGui.QFrame.Raised)
		
		# Object type of usage
		for i in self.useTypes:
			self.useTypeCombo.addItem(self.useTypes[i])
		self.useTypeCombo.currentIndexChanged.connect(self.changeUseType)
			
		self.populateUseTargetCombobox(0)
		
		self.useTextLabel = QtGui.QLabel("Teksti käytettäessä:")
		
		self.allTextsButton = QtGui.QPushButton("Nämä ja muut tekstit")
		self.allTextsButton.clicked.connect(self.showAllTexts)
		
		# Widgets used by doors
		self.doorTransitionLabel = QtGui.QLabel("Mihin ovesta pääsee?")
		self.doorTransitionCombo = QtGui.QComboBox(self)
		self.doorTransitionCombo.setIconSize(QtCore.QSize(50,50))
		self.populateRoomCombobox(self.doorTransitionCombo)
		self.doorTransitionLabelLine = self.createSeparator()
		
		self.openDoorImage = ObjectImageSettings("Avoin ovi", "Avoimen oven nimi", parent=self)
		self.closedDoorImage = ObjectImageSettings("Suljettu ovi", "Suljetun oven nimi", parent=self)
		self.lockedDoorImage = ObjectImageSettings("Lukittu ovi", "Lukitun oven nimi", True, "Onko ovi lukossa?", parent=self)
		
		# Container image widgets
		self.lockedContainerImage = ObjectImageSettings("Lukittu säilö", "Lukitun säilön nimi", True, "Onko säilö lukossa?", parent=self)
		self.fullContainerImage = ObjectImageSettings("Täysi säilö", "Avoimen säilön nimi", parent=self)
		self.emptyContainerImage = ObjectImageSettings("Tyhjä säilö", "Tyhjän säilön nimi", parent=self)

		
		# Used by all
		self.layout.addWidget(self.nameLabel)
		self.layout.addWidget(self.objectNameEdit)
		self.layout.addWidget(self.imgTextLabel)
		self.layout.addWidget(self.itemImage)
		
		# Room
		self.layout.addWidget(self.musicLabel)
		self.layout.addWidget(self.musicTextEdit)
		self.layout.addWidget(self.musicBtn)
		self.layout.addWidget(self.whereFromLabel)
		self.layout.addWidget(self.whereLocatedLabel)
		self.layout.addWidget(self.roomCombo)
		self.layout.addWidget(self.roomComboItem)
		
		# Items
		self.layout.addWidget(self.clickTextLabel)
		self.layout.addWidget(self.clickTextEdit)
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
		
		# Door
		# TODO: "Remove this image" button for door images?
		#		Erase locked image at some point if "locked" not checked
		self.layout.addWidget(self.doorTransitionLabelLine)
		self.layout.addWidget(self.doorTransitionLabel)
		self.layout.addWidget(self.doorTransitionCombo)
		
		self.layout.addWidget(self.openDoorImage)
		self.layout.addWidget(self.closedDoorImage)
		self.layout.addWidget(self.lockedDoorImage)
		
		self.layout.addWidget(self.lockedContainerImage)
		self.layout.addWidget(self.fullContainerImage)
		self.layout.addWidget(self.emptyContainerImage)
		
		# Which widgets are shown with each object
		self.itemSettings = {
			"Room": [
				self.imgTextLabel,
				self.itemImage,
				self.nameLabel,
				self.objectNameEdit,
				self.musicLabel,
				self.musicTextEdit,
				self.musicBtn,
				self.whereFromLabel
				# TODO: doorCombo for where from
			],
			"Item": [
				self.nameLabel,
				self.objectNameEdit,
				self.imgTextLabel,
				self.itemImage,
				self.clickTextLabel,
				self.clickTextEdit,
				self.pickupLabelLine,
				self.pickupLabel,
				self.pickupTextLabel,
				self.pickupTextEdit,
				self.pickupBlockLabel,
				self.pickupBlockCombo,
				self.useLabelLine,
				self.useLabel,
				self.useTypeCombo,
				self.useTargetCombo,
				self.useTextLabel,
				self.useTextEdit,
				self.allTextsButton,
				self.whereLocatedLabel,
				self.roomComboItem
			],
			"Object": [
				self.nameLabel,
				self.objectNameEdit,
				self.imgTextLabel,
				self.itemImage,
				self.clickTextLabel,
				self.clickTextEdit,
				self.whereLocatedLabel,
				self.roomCombo
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
			],
			"Container": [
				self.nameLabel,
				self.objectNameEdit,
				self.imgTextLabel,
				self.whereLocatedLabel,
				self.roomCombo,
				
				self.lockedContainerImage,
				self.fullContainerImage,
				self.emptyContainerImage
			],
			"Obstacle": [
			
			]
		}
		
		# Hide every widget
		for key in self.itemSettings:
			for item in self.itemSettings[key]:
				item.hide()
		
	def createSeparator(self):
		label = QtGui.QLabel("")
		label.setFrameStyle(QtGui.QFrame.HLine | QtGui.QFrame.Raised)
		return label
		
	# Set the input field values for rooms
	def setRoomOptions(self, room):
		# Room name
		self.setObjectName(room, "Huoneella")
		
		# Room background
		self.setRoomBackground(self.parent.getImageDir()+"/"+room.getBackground().getLocation())
		
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
		self.setItemImage(self.parent.getImageDir()+"/"+imageObject.getLocation())
		
		# Location
		self.setComboboxIndex(item.location, self.roomComboItem)
		
		# Examine text
		examineText = item.getExamineText()
		if not (examineText):
			examineText = ""
		self.clickTextEdit.setText(examineText)
		
		# Pickup text
		pickupText = item.getPickupText()
		if not (pickupText):
			pickupText = ""
		self.pickupTextEdit.setText(pickupText)
		
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
		useText = item.getUseText()
		if not (useText):
			useText = ""
		self.useTextEdit.setText(useText)
		
	# Set the input field values for generic objects
	def setGenericOptions(self, gObject):
		self.setObjectName(gObject, "Esineellä")
		
		imageObject = gObject.getRepresentingImage()
		self.setItemImage(self.parent.getImageDir()+"/"+imageObject.getLocation())
		
		# Location
		self.setComboboxIndex(gObject.location, self.roomCombo)
		
		# Examine text
		examineText = gObject.getExamineText()
		if not (examineText):
			examineText = ""
		self.clickTextEdit.setText(examineText)
		
	# Set the input field values for containers
	def setContainerOptions(self, container):
		self.setObjectName(container, "Säilöllä")
		
		imageObject = container.getRepresentingImage()
		self.setItemImage(self.parent.getImageDir()+"/"+imageObject.getLocation())
		
		self.lockedContainerImage.setSettings(container, container.lockedImage)
		self.fullContainerImage.setSettings(container, container.fullImage)
		self.emptyContainerImage.setSettings(container, container.emptyImage)
		
		# Location
		self.setComboboxIndex(container.location, self.roomCombo)
		
	# Set the input field values for obstacles
	def setObstacleOptions(self, obstacle):
		print("Obstacle options!")
		return
		
		
	# Set any game object name
	def setObjectName(self, image, textStart, textEdit=None):
		# Given image may be None
		try:
			name = image.getName()
		except AttributeError:
			name = ""
			
		if (name == None):
			name = "%s ei ole nimeä" %(textStart)
			
		# If textEdit is defined, set its text instead
		if (textEdit):
			textEdit.setText(name)
		else:
			self.objectNameEdit.setText(name)
		
	def setDoorOptions(self, doorObject):
		self.openDoorImage.setSettings(doorObject, doorObject.openImage)
		self.closedDoorImage.setSettings(doorObject, doorObject.closedImage)
		self.lockedDoorImage.setSettings(doorObject, doorObject.lockedImage)
		
		# Location
		self.setComboboxIndex(doorObject.location, self.roomCombo)
		
		# Door transition room
		self.setComboboxIndex(doorObject.transition, self.doorTransitionCombo)
		
	def showAllTexts(self):
		print("Clicked show all texts")
		
	# Change object use type
	def changeUseType(self, index):
		print("Change item use type", index)
		self.populateUseTargetCombobox(index)
		
	# Set object use type
	def setItemUse(self, typeIndex, useItem):
		self.useTypeCombo.setCurrentIndex(typeIndex)
		
		# Find the combobox item with the given item
		for i in range(self.useTargetCombo.count()):
			if (self.useTargetCombo.itemData(i) == useItem):
				self.useTargetCombo.setCurrentIndex(i)
				
	# Set object use target
	def setUseTarget(self, index):
		print("Use target set", self.useTargetCombo.itemData(index))
		
	def showMusicDialog(self):
		fname, _ = QtGui.QFileDialog.getOpenFileName(self,
		'Valitse musiikkitiedosto','~', "Musiikkitiedostot (*.mp3 *.ogg)")
		# TODO: Modified object requires filename in format "audio/filename.xxx"
		if (len(fname) != 0):
			self.musicTextEdit.setText(fname.split("/")[-1])
		
	def showImageDialog(self, callBack):
		fname, _ = QtGui.QFileDialog.getOpenFileName(self,
		'Valitse taustakuva','~', "Taustakuvat (*.png)")
		# TODO: Modified object requires filename in format "images/filename.png"
		
		if (len(fname) != 0):
			callBack(fname)
		
	# TODO: Is this obsolete?
	def setRoomBackground(self, imagePath):
		imgPixmap = QtGui.QPixmap(imagePath).scaled(200, 200, QtCore.Qt.KeepAspectRatio)
		self.itemImage.setPixmap(imgPixmap)
		
	def setItemImage(self, imagePath):
		imgPixmap = QtGui.QPixmap(imagePath)
		# TODO: Have spacing for smaller items
		if (imgPixmap.size().height() > 200):
			imgPixmap = imgPixmap.scaled(200, 200, QtCore.Qt.KeepAspectRatio)
		self.itemImage.setPixmap(imgPixmap)
		
	# Set the image of open, closed or locked door
	def setDoorImage(self, image, state):
		if (state == "locked"):
			doorImage = self.doorImageLocked
		elif (state == "closed"):
			doorImage = self.doorImageClosed
		elif (state == "open"):
			doorImage = self.doorImageOpen
		else:
			return
			
		if (image):
			imagePath = self.parent.getImageDir()+"/"+image.getLocation()
		else:
			imagePath = "images/door_placeholder.png"
			
		imgPixmap = QtGui.QPixmap(imagePath)
		if (imgPixmap.size().height() > 200):
			imgPixmap = imgPixmap.scaled(200, 200, QtCore.Qt.KeepAspectRatio)
		doorImage.setPixmap(imgPixmap)
		
	# Set the name of open, closed or locked door
	def setDoorName(self, state):
		if (state == "locked"):
			textStart = "Lukitulla ovella"
			textEdit = self.lockedDoorTextEdit
			doorObject = self.currentObject.lockedImage
		elif (state == "closed"):
			textStart = "Suljetulla ovella"
			textEdit = self.closedDoorTextEdit
			doorObject = self.currentObject.closedImage
		elif (state == "open"):
			textStart = "Avoimella ovella"
			textEdit = self.openDoorTextEdit
			doorObject = self.currentObject.openImage
		else:
			return
		print("SEt",doorObject,textStart)
		self.setObjectName(doorObject, textStart, textEdit)
			
	# Change door image after image dialog
	def changeDoorImage(self, state, imagePath):
		if (state == "locked"):
			doorImage = self.doorImageLocked
		elif (state == "closed"):
			doorImage = self.doorImageClosed
		elif (state == "open"):
			doorImage = self.doorImageOpen
		else:
			return
			
		imgPixmap = QtGui.QPixmap(imagePath)
		if (imgPixmap.size().height() > 200):
			imgPixmap = imgPixmap.scaled(200, 200, QtCore.Qt.KeepAspectRatio)
		doorImage.setPixmap(imgPixmap)
		
	# Sets the index of a combobox according to given targetObject
	def setComboboxIndex(self, targetObject, combobox):
		# Find the combobox item with the given item
		for i in range(self.roomCombo.count()):
			if (combobox.itemData(i) == targetObject):
				combobox.setCurrentIndex(i)
	
	# TODO: Door combobox
	
	# Create combobox from given items with default of all item types
	def createItemCombobox(self, objectTypes=None):
		if not (objectTypes):
			objectTypes = ("object", "item", "door", "container", "obstacle")
		
		combobox = QtGui.QComboBox(self)
		combobox.setIconSize(QtCore.QSize(50,50))
		
		self.populateCombobox(objectTypes, combobox)
		return combobox
		
	# Populate a given combobox with game rooms
	def populateRoomCombobox(self, combobox):
		for room in self.parent.getRoomObjects():
			# TODO: Some model to eliminate redundancy from getName/roomName patterns
			roomName = room.getName()
			if not (roomName):
				roomName = "Huoneella ei ole nimeä"
			imgPixmap = QtGui.QPixmap(self.parent.getImageDir()+"/"+room.getBackground().getLocation())
			
			roomIcon = QtGui.QIcon(imgPixmap)
			combobox.addItem(roomIcon, roomName, userData=room)
			
	# Populate use target combobox
	def populateUseTargetCombobox(self, useType):
		if (useType == 0):
			self.useTargetCombo.clear()
			return
		elif (useType == 1):
			objectTypes = ("item", "object")
		elif (useType == 2):
			objectTypes = ("door", "container")
		elif (useType == 3):
			objectTypes = ("container",)
		else:
			objectTypes = ("obstacle",)
			
		self.populateCombobox(objectTypes, self.useTargetCombo)
		
	# TODO: Create a combo icon of multi-part objects such as cieni
	#		(those with "related" attribute)
	def populateBlockingCombobox(self):
		self.pickupBlockCombo.addItem("Ei estä")
		self.populateCombobox(("obstacle",), self.pickupBlockCombo)
					
	# Populate a given combobox with given types of objects
	# categorized by game rooms
	def populateCombobox(self, objectTypes, combobox):
		# TODO: Disconnect combobox from events when populating it
		combobox.clear()
		combobox.addItem("Ei valittu")
		
		for objType in objectTypes:
			objRooms = self.parent.getObjectsByType(objType)
			
			# Combobox has rooms with their obstacles under them
			for room in objRooms:
				print("room", room)
				roomObject = room["room"]
				roomName = roomObject.getName()
				if not (roomName):
					roomName = "Huoneella ei ole nimeä"
				imgPixmap = QtGui.QPixmap(self.parent.getImageDir()+"/"+roomObject.getBackground().getLocation())
				roomIcon = QtGui.QIcon(imgPixmap)
				
				# TODO: Disable ability to choose rooms
				combobox.addItem(roomIcon, roomName)
				
				# TODO: Indendation of objects in the combobox
				# Add objects under the room
				for obj in room["objects"]:
					# Don't display the triggering item itself
					if (obj == self.currentObject):
						continue
					if (obj.getClassname() == "Text"):
						continue
					
					imageObject = obj.getRepresentingImage()
					imgPixmap = QtGui.QPixmap(self.parent.getImageDir()+"/"+imageObject.getLocation())
					targetIcon = QtGui.QIcon(imgPixmap)
					combobox.addItem(targetIcon, imageObject.getName(), userData=obj)
