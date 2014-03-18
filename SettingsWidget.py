from PySide import QtGui, QtCore

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
		self.populateroomCombobox(self.roomCombo)
		
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
		
		# Widgets required by door settings
		self.openDoorLabelLine = self.createSeparator()
		self.openDoorLabel = QtGui.QLabel("Avoin ovi")
		self.openDoorTextLabel = QtGui.QLabel("Avoimen oven nimi")
		self.openDoorTextEdit = QtGui.QLineEdit()
		self.doorImageOpen = QtGui.QLabel(self)
		self.doorImageOpen.mousePressEvent = lambda s: self.showImageDialog(lambda imagePath: self.changeDoorImage("open", imagePath))
		self.openDoorClickTextLabel = QtGui.QLabel("Teksti klikatessa")
		self.openDoorClickTextEdit = QtGui.QTextEdit()
		self.openDoorClickTextEdit.setMaximumHeight(50)
		
		self.closedDoorLabelLine = self.createSeparator()
		self.closedDoorLabel = QtGui.QLabel("Suljettu ovi")
		self.closedDoorTextLabel = QtGui.QLabel("Suljetun oven nimi")
		self.closedDoorTextEdit = QtGui.QLineEdit()
		self.doorImageClosed = QtGui.QLabel(self)
		self.doorImageClosed.mousePressEvent = lambda s: self.showImageDialog(lambda imagePath: self.changeDoorImage("closed", imagePath))
		self.closedDoorClickTextLabel = QtGui.QLabel("Teksti klikatessa")
		self.closedDoorClickTextEdit = QtGui.QTextEdit()
		self.closedDoorClickTextEdit.setMaximumHeight(50)
		
		self.lockedDoorLabelLine = self.createSeparator()
		self.lockedDoorLabel = QtGui.QLabel("Lukittu ovi")
		self.lockedDoorTextLabel = QtGui.QLabel("Lukitun oven nimi")
		self.lockedDoorTextEdit = QtGui.QLineEdit()
		self.doorImageLocked = QtGui.QLabel(self)
		self.doorImageLocked.mousePressEvent = lambda s: self.showImageDialog(lambda imagePath: self.changeDoorImage("locked", imagePath))
		self.lockedDoorClickTextLabel = QtGui.QLabel("Teksti klikatessa")
		self.lockedDoorClickTextEdit = QtGui.QTextEdit()
		self.lockedDoorClickTextEdit.setMaximumHeight(50)
		
		self.doorTransitionLabel = QtGui.QLabel("Mihin ovesta pääsee?")
		self.doorTransitionCombo = QtGui.QComboBox(self)
		self.doorTransitionCombo.setIconSize(QtCore.QSize(50,50))
		self.populateroomCombobox(self.doorTransitionCombo)
		self.doorTransitionLabelLine = self.createSeparator()
		
		self.lockedDoorLockedCheckbox = QtGui.QCheckBox("Onko ovi lukossa?")
		self.lockedDoorLockedCheckbox.stateChanged.connect(self.changeDoorLocked)
		
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
		self.layout.addWidget(self.openDoorLabelLine)
		self.layout.addWidget(self.openDoorLabel)
		self.layout.addWidget(self.openDoorTextLabel)
		self.layout.addWidget(self.openDoorTextEdit)
		self.layout.addWidget(self.doorImageOpen)
		self.layout.addWidget(self.openDoorClickTextLabel)
		self.layout.addWidget(self.openDoorClickTextEdit)
		
		self.layout.addWidget(self.lockedDoorLabelLine)
		self.layout.addWidget(self.lockedDoorLabel)
		self.layout.addWidget(self.lockedDoorLockedCheckbox)
		self.layout.addWidget(self.lockedDoorTextLabel)
		self.layout.addWidget(self.lockedDoorTextEdit)
		self.layout.addWidget(self.doorImageLocked)
		self.layout.addWidget(self.doorImageLocked)
		self.layout.addWidget(self.lockedDoorClickTextLabel)
		self.layout.addWidget(self.lockedDoorClickTextEdit)
		
		self.layout.addWidget(self.closedDoorLabelLine)
		self.layout.addWidget(self.closedDoorLabel)
		self.layout.addWidget(self.closedDoorTextLabel)
		self.layout.addWidget(self.closedDoorTextEdit)
		self.layout.addWidget(self.doorImageClosed)
		self.layout.addWidget(self.closedDoorClickTextLabel)
		self.layout.addWidget(self.closedDoorClickTextEdit)
		
		self.layout.addWidget(self.doorTransitionLabelLine)
		self.layout.addWidget(self.doorTransitionLabel)
		self.layout.addWidget(self.doorTransitionCombo)
		
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
				self.roomCombo
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
				self.nameLabel,
				self.objectNameEdit,
				
				self.whereLocatedLabel,
				self.roomCombo,
				
				self.openDoorLabelLine,
				self.openDoorLabel,
				self.openDoorTextLabel,
				self.openDoorTextEdit,
				self.doorImageOpen,
				self.openDoorClickTextLabel,
				self.openDoorClickTextEdit,
				
				self.lockedDoorLabelLine,
				self.lockedDoorLabel,
				self.lockedDoorLockedCheckbox,
				self.lockedDoorTextLabel,
				self.lockedDoorTextEdit,
				self.doorImageLocked,
				self.lockedDoorClickTextLabel,
				self.lockedDoorClickTextEdit,
				
				self.closedDoorLabelLine,
				self.closedDoorLabel,
				self.closedDoorTextLabel,
				self.closedDoorTextEdit,
				self.doorImageClosed,
				self.closedDoorClickTextLabel,
				self.closedDoorClickTextEdit,
				
				self.doorTransitionLabelLine,
				self.doorTransitionLabel,
				self.doorTransitionCombo
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
		
	# Set settings for the room view
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
		
	# Create the input fields for object options
	def setItemOptions(self, item):
		imageObject = item.getRepresentingImage()
		
		# Object name
		self.setObjectName(imageObject, "Esineellä")
		
		# Item image
		self.setItemImage(self.parent.getImageDir()+"/"+imageObject.getLocation())
		
		# Location
		self.setItemLocation(item)
		
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
		
	# Create the input fields for generic objects
	def setGenericOptions(self, gObject):
		self.setObjectName(gObject, "Esineellä")
		
		imageObject = gObject.getRepresentingImage()
		self.setItemImage(self.parent.getImageDir()+"/"+imageObject.getLocation())
		
		# Location
		self.setItemLocation(gObject)
		
		# Examine text
		examineText = gObject.getExamineText()
		if not (examineText):
			examineText = ""
		self.clickTextEdit.setText(examineText)
		
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
		# Set the locked door field state enabled or disabled
		if (doorObject.closedImage):
			self.lockedDoorLockedCheckbox.setCheckState(QtCore.Qt.CheckState.Checked)
		else:
			self.lockedDoorLockedCheckbox.setCheckState(QtCore.Qt.CheckState.Unchecked)
		self.changeDoorLocked()
		
		# Set images for each door found
		self.setDoorImage(doorObject.openImage, "open")
		self.setDoorImage(doorObject.closedImage, "closed")
		self.setDoorImage(doorObject.lockedImage, "locked")
		
		# Set names for each door image
		self.setDoorName("open")
		self.setDoorName("closed")
		self.setDoorName("locked")
		
		# Location
		self.setItemLocation(doorObject)
		
		# Examine text
		examineText = doorObject.getExamineText()
		if not (examineText):
			examineText = ""
		self.clickTextEdit.setText(examineText)	
	
	# Changes door locked input fields according to the checkbox state
	def changeDoorLocked(self):
		if (self.lockedDoorLockedCheckbox.isChecked()):
			isDisabled = False
		else:
			isDisabled = True
			
		self.lockedDoorTextLabel.setDisabled(isDisabled)
		self.lockedDoorTextEdit.setDisabled(isDisabled)
		self.doorImageLocked.setDisabled(isDisabled)
		self.lockedDoorClickTextLabel.setDisabled(isDisabled)
		self.lockedDoorClickTextEdit.setDisabled(isDisabled)
		
		# TODO: Erase locked image, name etc. when unchecked
		
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
		
	def setItemLocation(self, item):
		# Find the combobox item with the given item
		for i in range(self.roomCombo.count()):
			if (self.roomCombo.itemData(i) == item.location):
				self.roomCombo.setCurrentIndex(i)
	
	# TODO: Door combobox
	
	# Populate a given combobox with game rooms
	def populateroomCombobox(self, combobox):
		for room in self.parent.getRoomObjects():
			# TODO: Some model to eliminate redundancy from getName/roomName patterns
			roomName = room.getName()
			if not (roomName):
				roomName = "Huoneella ei ole nimeä"
			imgPixmap = QtGui.QPixmap(self.parent.getImageDir()+"/"+room.getBackground().getLocation())
			
			roomIcon = QtGui.QIcon(imgPixmap)
			combobox.addItem(roomIcon, roomName, userData=room)
			
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
				roomObject = room["room"]
				roomName = roomObject.getName()
				if not (roomName):
					roomName = "Huoneella ei ole nimeä"
				imgPixmap = QtGui.QPixmap(self.parent.getImageDir()+"/"+roomObject.getBackground().getLocation())
				roomIcon = QtGui.QIcon(imgPixmap)
				
				# TODO: Disable ability to choose rooms
				self.useTargetCombo.addItem(roomIcon, roomName)
				
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
