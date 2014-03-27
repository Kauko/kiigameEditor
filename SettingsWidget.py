from PySide import QtGui, QtCore
from ObjectImageSettings import ObjectImageSettings
from ImageCache import ImageCache

# Item and room settings widget used in editor
class SettingsWidget(QtGui.QWidget):
	def __init__(self, parent=None):
		super(SettingsWidget, self).__init__(parent)
		
		self.currentObject = None
		self.lastObjectType = None
		self.useTypes = {0: "Ei käyttöä", 1: "Käytä toiseen esineeseen",
			2: "Avaa jotakin", 3: "Laita johonkin", 4: "Ota jostakin", 5: "Poista este"}
			
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
		self.whereFromLabel = QtGui.QLabel("Mistä kulkureiteistä tänne pääsee?")
		# TODO: whereFromCombo
		
		self.examineTextLabel = QtGui.QLabel("Teksti klikatessa:")
		self.examineTextEdit = QtGui.QTextEdit()
		self.examineTextEdit.setMaximumHeight(50)
		self.examineTextEdit.focusOutEvent = lambda s: self.changeExamineText()
		
		# Pickup text section
		self.pickupLabel = QtGui.QLabel("Poiminta")
		self.pickupLabelLine = self.createSeparator()
		self.pickupLabelLine.setFrameStyle(QtGui.QFrame.HLine | QtGui.QFrame.Raised)
		self.pickupTextLabel = QtGui.QLabel("Teksti poimiessa:")
		
		self.pickupTextEdit = QtGui.QTextEdit()
		self.pickupTextEdit.setMaximumHeight(50)
		self.pickupTextEdit.focusOutEvent = lambda s: self.changePickupText()
		
		# Object usage
		self.useLabel = QtGui.QLabel("Käyttö")
		self.useLabelLine = self.createSeparator()
		
		# Object type of usage
		self.useTypeCombo = QtGui.QComboBox(self)
		for i in self.useTypes:
			self.useTypeCombo.addItem(self.useTypes[i])
		self.useTypeCombo.currentIndexChanged.connect(self.changeItemUseType)
		
		self.useTextLabel = QtGui.QLabel("Teksti käytettäessä:")
		
		# Use target
		self.useTargetCombo = self.createItemCombobox("Ei valittu", connectTo=self.changeUseTarget)
		
		self.allTextsButton = QtGui.QPushButton("Nämä ja muut tekstit")
		self.allTextsButton.clicked.connect(self.showAllTexts)
		
		# Door widgets
		self.doorTransitionLabel = QtGui.QLabel("Mihin pääsee?")
		self.doorTransitionCombo = self.createItemCombobox("Ei mihinkään", "room", connectTo=self.changeDoorTransition)
		#self.doorTransitionLabelLine = self.createSeparator()
		
		self.doorInitialStateLabel = QtGui.QLabel("Tila alussa")
		self.doorInitialStateCombo = QtGui.QComboBox(self)
		self.doorInitialStateCombo.addItem("Kiinni")
		self.doorInitialStateCombo.addItem("Auki")
		self.doorInitialStateCombo.currentIndexChanged.connect(lambda s: self.objectComboboxHandler(self.doorInitialStateCombo, self.changeDoorInitialState))
		
		self.openDoorImage = ObjectImageSettings("Avoin kulkureitti", "Avoimen kulkureitin nimi", parent=self)
		self.closedDoorImage = ObjectImageSettings("Suljettu kulkureitti", "Suljetun kulkureitin nimi", parent=self)
		self.lockedDoorImage = ObjectImageSettings("Lukittu kulkureitti", "Lukitun kulkureitin nimi", True, "Lukossa", parent=self)
		
		# Container widgets
		self.lockedContainerImage = ObjectImageSettings("Lukittu säiliö", "Lukitun säiliön nimi", True, "Lukossa", parent=self)
		self.fullContainerImage = ObjectImageSettings("Täysi säiliö", "Avoimen säiliön nimi", parent=self)
		self.emptyContainerImage = ObjectImageSettings("Tyhjä säiliö", "Tyhjän säiliön nimi", parent=self)
		
		# Obstacle widgets
		self.obstacleImage = ObjectImageSettings(None, "Esteen nimi", False, parent=self)
		self.obstacleBlocksLabel = QtGui.QLabel("Mitä estää?")
		self.obstacleBlocksCombo = self.createItemCombobox("Ei mitään", ("door",), ("door",), noChoiceMethod=self.clearObstacleBlock, connectTo=self.changeObstacleBlock)
		
		self.whatGoesLabel = QtGui.QLabel("Mikä menee säiliöön?")
		self.whatGoesCombo = self.createItemCombobox("Ei mikään", ("item",), ("item",), connectTo=self.changeWhatGoes)
		
		self.whatComesLabel = QtGui.QLabel("Mitä tulee säiliöstä?")
		self.whatComesCombo = self.createItemCombobox("Ei mitään", ("item",), ("item",), connectTo=self.changeWhatComes)
		
		self.useConsumeCheckbox = QtGui.QCheckBox() # Set text afterwards
		self.useConsumeCheckbox.stateChanged.connect(self.changeUseConsume)
		
		self.outcomeLabel = QtGui.QLabel("Lopputulos")
		self.outcomeCombobox = self.createItemCombobox("Ei valittu", ("object",), ("object",), noChoiceMethod=self.clearOutcome, connectTo=self.changeOutcome)
		
		self.layout.addWidget(self.nameLabel)
		self.layout.addWidget(self.objectNameEdit)
		self.layout.addWidget(self.imgTextLabel)
		self.layout.addWidget(self.objectImage)
		
		self.layout.addWidget(self.musicLabel)
		self.layout.addWidget(self.musicTextEdit)
		self.layout.addWidget(self.musicBtn)
		self.layout.addWidget(self.musicClear)
		self.layout.addWidget(self.whereFromLabel)
		
		self.layout.addWidget(self.examineTextLabel)
		self.layout.addWidget(self.examineTextEdit)
		self.layout.addWidget(self.pickupLabelLine)
		self.layout.addWidget(self.pickupLabel)
		self.layout.addWidget(self.pickupTextLabel)
		self.layout.addWidget(self.pickupTextEdit)
		
		self.layout.addWidget(self.useLabelLine)
		self.layout.addWidget(self.useLabel)
		self.layout.addWidget(self.useTypeCombo)
		self.layout.addWidget(self.useTargetCombo)
		
		self.layout.addWidget(self.useConsumeCheckbox)
		self.layout.addWidget(self.outcomeLabel)
		self.layout.addWidget(self.outcomeCombobox)
		
		self.layout.addWidget(self.useTextLabel)
		self.layout.addWidget(self.useTextEdit)
		self.layout.addWidget(self.allTextsButton)
		
		#self.layout.addWidget(self.doorTransitionLabelLine)
		self.layout.addWidget(self.doorTransitionLabel)
		self.layout.addWidget(self.doorTransitionCombo)
		
		self.layout.addWidget(self.doorInitialStateLabel)
		self.layout.addWidget(self.doorInitialStateCombo)
		
		self.layout.addWidget(self.closedDoorImage)
		self.layout.addWidget(self.lockedDoorImage)
		self.layout.addWidget(self.openDoorImage)
		
		self.layout.addWidget(self.whatGoesLabel)
		self.layout.addWidget(self.whatGoesCombo)
		self.layout.addWidget(self.whatComesLabel)
		self.layout.addWidget(self.whatComesCombo)
		
		self.layout.addWidget(self.fullContainerImage)
		self.layout.addWidget(self.lockedContainerImage)
		self.layout.addWidget(self.emptyContainerImage)
		
		self.layout.addWidget(self.obstacleBlocksLabel)
		self.layout.addWidget(self.obstacleBlocksCombo)
		self.layout.addWidget(self.obstacleImage)
		
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
				self.useConsumeCheckbox,
				self.outcomeLabel,
				self.outcomeCombobox
			],
			"Object": [
				self.nameLabel,
				self.objectNameEdit,
				self.imgTextLabel,
				self.objectImage,
				self.examineTextLabel,
				self.examineTextEdit,
			],
			"Door": [
				#self.doorTransitionLabelLine,
				self.doorTransitionLabel,
				self.doorTransitionCombo,
				
				self.doorInitialStateLabel,
				self.doorInitialStateCombo,
				
				self.openDoorImage,
				self.closedDoorImage,
				self.lockedDoorImage
			],
			"Container": [
				self.lockedContainerImage,
				self.fullContainerImage,
				self.emptyContainerImage,
				
				self.whatGoesLabel,
				self.whatGoesCombo,
				self.whatComesLabel,
				self.whatComesCombo
			],
			"Obstacle": [
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
		
		# Examine text
		self.setExamineText(self.currentObject)
		
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
			useType = 5
		elif (itemTargetType in ("Door", "Container")):
			# Item may unlock door or container or may go into a container
			if (itemTarget.key == item):
				useType = 2
			else:
				try:
					if (itemTarget.inItem == item):
						useType = 3
				except AttributeError:
					pass
					
				try:
					if (itemTarget.outItem == item):
						useType = 4
				except AttributeError:
					pass
					
		self.setUseConsume()
		
		self.setItemUseType(useType)
		self.setItemUseTarget(itemTarget)
		self.setItemOutcome(self.currentObject.outcome)
		self.setUseText()
			
	# Set the input field values for generic objects
	def setGenericOptions(self, gObject):
		self.setObjectName(gObject, "Esineellä")
		
		imageObject = gObject.getRepresentingImage()
		self.setobjectImage(self.parent.getImageDir()+"/"+imageObject.getSource())
		
		# Examine text
		self.setExamineText(self.currentObject)
			
	# Set the input field values for containers
	def setContainerOptions(self, container):
	
		# Set image settings for each image
		self.lockedContainerImage.setSettings(container, container.lockedImage)
		self.fullContainerImage.setSettings(container, container.fullImage)
		self.emptyContainerImage.setSettings(container, container.emptyImage)
		
		# Set what goes, what comes from the container
		self.setComboboxIndex(container.inItem, self.whatGoesCombo)
		self.setComboboxIndex(container.outItem, self.whatComesCombo)
		
	# Set the input field values for obstacles
	def setObstacleOptions(self, obstacle):
		self.obstacleImage.setSettings(obstacle, obstacle.blockingImage)
		
	def setobjectImage(self, imagePath, objectImage=None):
		imgPixmap = self.imageCache.createPixmap(imagePath)
		
		# TODO: Have spacing for smaller items
		if (imgPixmap.size().height() > 200):
			imgPixmap = imgPixmap.scaled(200, 200, QtCore.Qt.KeepAspectRatio)
			
		if (objectImage):
			objectImage.setPixmap(imgPixmap)
		else:
			self.objectImage.setPixmap(imgPixmap)
		
	# Set item use type
	def setItemUseType(self, typeIndex):
		self.useTypeCombo.setCurrentIndex(typeIndex)
		
		self.updateUseTargetCombobox(typeIndex, self.useTargetCombo)
		
		# Show extra options when selecting use on other object
		if (typeIndex == 1):
			self.useConsumeCheckbox.setText("Katoaako %s käytettäessä?" %(self.currentObject.getName()))
			self.useConsumeCheckbox.show()
			self.outcomeLabel.show()
			self.outcomeCombobox.show()
		else:
			self.useConsumeCheckbox.hide()
			self.outcomeLabel.hide()
			self.outcomeCombobox.hide()
			
		# When no use, hide and clear elements
		if (typeIndex == 0):
			self.useTargetCombo.hide()
			self.useTextLabel.hide()
			self.useTextEdit.hide()
			self.useTextEdit.clear()
			self.changeUseText()
			self.allTextsButton.hide()
			
			self.currentObject.clearTarget()
		else:
			self.useTargetCombo.show()
			self.useTextLabel.show()
			self.useTextEdit.show()
			self.allTextsButton.show()
			
	#  Set item use target
	def setItemUseTarget(self, useItem):
		if (useItem):
			# Find the combobox item with the given item
			for i in range(self.useTargetCombo.count()):
				if (self.useTargetCombo.itemData(i) == useItem):
					self.useTargetCombo.setCurrentIndex(i)
					return
		self.useTargetCombo.setCurrentIndex(0)
		
	def setItemOutcome(self, outcomeItem):
		if (outcomeItem):
			# Find the combobox item with the given item
			for i in range(self.outcomeCombobox.count()):
				if (self.outcomeCombobox.itemData(i) == outcomeItem):
					self.outcomeCombobox.setCurrentIndex(i)
					return
					
		self.outcomeCombobox.setCurrentIndex(0)
				
	# TODO: Door needs "who blocks" field?
	def setDoorOptions(self, doorObject):
		# Set each image's settings
		self.openDoorImage.setSettings(doorObject, doorObject.openImage)
		self.closedDoorImage.setSettings(doorObject, doorObject.closedImage)
		self.lockedDoorImage.setSettings(doorObject, doorObject.lockedImage)
		
		# Door transition room
		self.setComboboxIndex(doorObject.transition, self.doorTransitionCombo)
		
	# Set use item for items
	def setUseText(self, textEdit=None, item=None):
		if (self.useTypeCombo.currentIndex() == 0):
			return
			
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
	def setExamineText(self, gameObject, textEdit=None):
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
		
	def setUseConsume(self):
		isConsumed = self.useConsumeCheckbox.isChecked()
		self.currentObject.setConsume(isConsumed)
		
		if (isConsumed):
			self.useConsumeCheckbox.setCheckState(QtCore.Qt.CheckState.Checked)
		else:
			self.useConsumeCheckbox.setCheckState(QtCore.Qt.CheckState.Unchecked)
			
	def changeWhereLocated(self, combobox):
		print("Change where located to",combobox.itemData(combobox.currentIndex()))
		
	# Text that comes after using an item
	def changeUseText(self):
		# TODO: Disable text field if no target is selected
		self.currentObject.setUseText(self.useTextEdit.toPlainText())
		
	def changePickupText(self):
		self.currentObject.setPickupText(self.pickupTextEdit.toPlainText())
		
	def changeExamineText(self, textEdit=None, gameObject=None):
		if not (gameObject):
			gameObject = self.currentObject
			
		if not (textEdit):
			textEdit = self.examineTextEdit
			
		gameObject.setExamineText(textEdit.toPlainText())
		
	# TODO: Need setDoorInitialState()
	def changeDoorInitialState(self):
		print("Change door initial state", self.doorInitialStateCombo.currentIndex())
		
		# Initially closed, all states are possible
		if (self.doorInitialStateCombo.currentIndex() == 0):
			self.closedDoorImage.setDisabled(False)
			self.lockedDoorImage.setDisabled(False)
			self.openDoorImage.setDisabled(False)
		# Initially open, only possible state is open
		else:
			self.closedDoorImage.setDisabled(True)
			self.lockedDoorImage.setDisabled(True)
			self.openDoorImage.setDisabled(False)
			
			# Remove door's closed and locked images
			self.currentObject.setClosed(False)
			self.currentObject.setLocked(False)
			
	# Change the image of a gameobject
	def changeObjectImage(self, imagePath, image=None, gameObject=None):
		# If no image, a default image var will be used
		self.setobjectImage(imagePath, image)
		
		if not (gameObject):
			gameObject = self.currentObject
		gameObject.getRepresentingImage().setSource(imagePath)
		
		self.updateParent()
		# TODO: Cannot use editor's images folder because of path edits
		#		-> make every path absolute, they should be cut only in the end
		
	# Change music
	def changeMusic(self, imagePath):
		self.currentObject.setMusic(imagePath)
		
	def changeUseConsume(self):
		self.currentObject.setConsume(self.useConsumeCheckbox.isChecked())
		
	def changeOutcome(self):
		self.currentObject.setOutcome(self.outcomeCombobox.itemData(self.outcomeCombobox.currentIndex()))
		
	def clearOutcome(self):
		self.currentObject.setOutcome(None)
		
	def clearUseTarget(self):
		print("Clear useTarget!")
		
	def changeObstacleBlock(self):
		self.currentObject.setBlockTarget(self.obstacleBlocksCombo.itemData(self.obstacleBlocksCombo.currentIndex()))
		
	def clearObstacleBlock(self):
		self.currentObject.clearBlockTarget()
		
	def changeWhatGoes(self):
		print("Change what goes!")
		self.currentObject.setInItem(self.whatGoesCombo.itemData(self.whatGoesCombo.currentIndex()))
		
	def clearWhatGoes(self):
		self.currentObject.clearInItem()
		
	def changeWhatComes(self):
		print("Change what comes!")
		self.currentObject.setOutItem(self.whatComesCombo.itemData(self.whatComesCombo.currentIndex()))
	
	def clearWhatComes(self):
		self.currentObject.clearOutItem()
	
	def changeDoorTransition(self):
		print("Change room transition!", self.doorTransitionCombo.itemData(self.doorTransitionCombo.currentIndex()))
		self.currentObject.setTransition(self.doorTransitionCombo.itemData(self.doorTransitionCombo.currentIndex()))
		
	def changeName(self, textEdit=None, gameObject=None):
		if not (gameObject):
			gameObject = self.currentObject
			
		if (textEdit):
			text = textEdit.text()
		else:
			text = self.objectNameEdit.text()
			
		# TODO: Get all other adessives like this too
		if (len(text) == 0):
			text = "%s ei ole nimeä" %(gameObject.generalNameAdessive)
			
		gameObject.setName(text)
		self.updateParent()
		
	# Update parent tab elements
	def updateParent(self):
		if (self.currentObject.__class__.__name__ == "Room"):
			self.parent.drawRooms()
		else:
			self.parent.drawRoomItems()
		
	# Change object use type
	def changeItemUseType(self, index):
		#  typeIndex, useItem) setItemUseType
		self.setItemUseType(index)
		self.setItemUseTarget(None)
		self.setItemOutcome(None)
		
	# Set item use target
	def changeUseTarget(self):
		index = self.useTargetCombo.currentIndex()
		
		targetType = self.useTargetCombo.itemData(index).__class__.__name__ 
		selectedObject = self.useTargetCombo.itemData(index)
		
		objectRole = 0
		useType = self.useTypeCombo.currentIndex()
		if (targetType in ("Door", "Container")):
			# Unlock something and target object is not set into locked state
			if (useType == 2 ):
				# TODO: Really nullify old key?
				# Get old current object's key and nullify it
				self.currentObject.clearTarget()
				
				# Nullify selected door's key
				if (self.useTargetCombo.itemData(index).key):
					self.useTargetCombo.itemData(index).key.clearTarget()
					
				# TODO: Get imagePath for door too from some better place
				# Set the object to be locked with new key
				imagePath = "images/container_placeholder.png"
				selectedObject.setLocked(True, imagePath, self.currentObject)
				
			# Put into container
			elif (useType == 3):
				objectRole = 1
				
			# Get from container
			elif (useType == 4):
				objectRole = 2
				
		self.currentObject.setTargetObject(selectedObject, objectRole)
		self.setUseText()
		
	# Create new game object
	def createObject(self, objectType):
		print("Create new object of type", objectType)
	
	def showAllTexts(self):
		print("Clicked show all texts")
		
	def clearMusic(self):
		self.currentObject.clearMusic()
		self.musicTextEdit.clear()
		
	# Sets the index of a combobox according to given targetObject
	def setComboboxIndex(self, targetObject, combobox):
		# Find the combobox item with the given item
		for i in range(combobox.count()):
			if (combobox.itemData(i) == targetObject):
				combobox.setCurrentIndex(i)
				return
		combobox.setCurrentIndex(0)
		
	# Create combobox from given items with default of all item types
	def createItemCombobox(self, noChoiceText, objectTypes=None, addChoices=None, noChoiceMethod=None, connectTo=None):
		if not (objectTypes):
			objectTypes = ("object", "item", "door", "container", "obstacle")
			
		combobox = QtGui.QComboBox(self)
		combobox.setIconSize(QtCore.QSize(50,50))
		
		if (objectTypes == "room"):
			self.populateRoomCombobox(combobox, addChoices)
		else:
			self.populateCombobox(objectTypes, combobox, noChoiceText, addChoices, noChoiceMethod)
		combobox.currentIndexChanged.connect(lambda s: self.objectComboboxHandler(combobox, connectTo))
		
		return combobox
		
	# Populate a given combobox with game rooms
	def populateRoomCombobox(self, combobox, addChoice=True):
		if (addChoice):
			imgPixmap = self.imageCache.createPixmap("images/add_new_icon.png")
			combobox.addItem(imgPixmap, "Lisää uusi huone")
			
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
		elif (useType == 3 or useType == 4):
			objectTypes = ("container",)
		elif (useType == 5):
			objectTypes = ("obstacle",)
			
		self.populateCombobox(objectTypes, combobox, "Ei valittu", objectTypes, self.clearUseTarget)
		
	# Handle item combobox
	def objectComboboxHandler(self, combobox, callback):
		
		#print("Choice handler", combobox, callback, combobox.itemData(combobox.currentIndex()))
		target = combobox.itemData(combobox.currentIndex())
		targetType = target.__class__.__name__
		
		# If chosen item is something else than a game object don't do callback
		if (targetType == "method"):
			target()
		elif (targetType == "str"):
			self.createObject(target)
		else:
			callback()
			
	# Populate a given combobox with given types of objects
	# categorized by game rooms
	def populateCombobox(self, objectTypes, combobox, noChoiceText=None, addChoices=None, noChoiceMethod=None):
		# TODO: Disconnect combobox from events when populating it
		combobox.clear()
		
		itemCounter = 0
		
		# Add the given string as the first item
		if (noChoiceText):
			imgPixmap = self.imageCache.createPixmap("images/no_choice_icon.png")
			combobox.addItem(imgPixmap, noChoiceText, userData=noChoiceMethod)
			itemCounter = 1
			
		# Add items to add given types of objects
		if (addChoices):
			imgPixmap = self.imageCache.createPixmap("images/add_new_icon.png")
			for choice in addChoices:
				combobox.addItem(imgPixmap, "Lisää uusi %s" %(self.parent.getGeneralName(choice).lower()), userData=choice)
				itemCounter += 1
			
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

