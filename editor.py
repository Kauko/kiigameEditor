# -*- coding: UTF-8 -*-

# TODO: Pre-cache rooms, images, texts etc. ?

from PySide import QtGui, QtCore
import ScenarioData

class Editor(QtGui.QMainWindow):
	def __init__(self, parent=None):
		super(Editor, self).__init__(parent)
		
		self.scenarioData = ScenarioData.ScenarioData()
		self.scenarioData.loadScenario()

		self.setWindowTitle("Kiigame - Pelieditori")
		
		# TODO: Menubar
		menubar = self.menuBar()
		
		tabWidget = QtGui.QTabWidget()
		self.setCentralWidget(tabWidget)
		
		self.createMainTab()
		self.createSpaceTab()
		
		tabWidget.addTab(self.mainTab, "Päänäkymä")
		tabWidget.addTab(self.spaceTab, "Tila")
		
	def createMainTab(self):
		self.mainTab = QtGui.QWidget()
		
		layout = QtGui.QHBoxLayout()
		self.mainTab.setLayout(layout)
		
		# Room preview
		left_frame = QtGui.QGroupBox("Huoneet")
		left_frame_layout = QtGui.QGridLayout()
		left_frame.setLayout(left_frame_layout)
		layout.addWidget(left_frame)
		
		# Set-up widget for showing rooms
		self.left_scene = QtGui.QListWidget(self)
		self.left_scene.setIconSize(QtCore.QSize(200, 200))
		self.left_scene.setViewMode(QtGui.QListView.IconMode)
		self.left_scene.setFlow(QtGui.QListView.LeftToRight)
		self.left_scene.setMovement(QtGui.QListView.Static)
		self.left_scene.itemClicked.connect(self.roomClicked)
		# TODO: Double click room, display the room view
		
		left_frame_layout.addWidget(self.left_scene)
		
		# Draw rooms and select the first one
		self.drawRooms()
		selectedRoom = self.left_scene.itemAt(0, 0)
		self.left_scene.setCurrentItem(selectedRoom)
		
		# Room items
		middle_frame = QtGui.QGroupBox("Huoneen esineet")
		middle_frame_layout = QtGui.QVBoxLayout()
		middle_frame.setLayout(middle_frame_layout)
		layout.addWidget(middle_frame)
		
		# Set-up widget for showing room items
		self.middle_scene = QtGui.QListWidget(self)
		self.middle_scene.setIconSize(QtCore.QSize(100, 100))
		self.middle_scene.setMovement(QtGui.QListView.Static)
		self.middle_scene.itemClicked.connect(self.roomItemClicked)
		
		middle_frame_layout.addWidget(self.middle_scene)
		
		self.drawRoomItems(selectedRoom.room.getItems())
		#selectedItem = self.middle_scene.itemAt(0, 0)
		#self.middle_scene.setCurrentItem(selectedItem)
		
		# Settings for items and rooms
		right_frame = QtGui.QGroupBox("Asetukset")
		right_frame_layout = QtGui.QVBoxLayout()
		right_frame.setLayout(right_frame_layout)
		layout.addWidget(right_frame)
		
		self.settingsWidget = SettingsWidget(self)
		right_frame_layout.addWidget(self.settingsWidget)
		
		self.settingsWidget.setRoomOptions(selectedRoom.room)
		
	def createSpaceTab(self):
		self.spaceTab = QtGui.QWidget()

		layout = QtGui.QHBoxLayout()
		self.spaceTab.setLayout(layout)

		# Room
		left_frame = QtGui.QGroupBox("Huone")
		left_frame_layout = QtGui.QVBoxLayout()
		left_frame.setLayout(left_frame_layout)
		layout.addWidget(left_frame)

		# Display room image
		scene = QtGui.QGraphicsScene(self)
		view = QtGui.QGraphicsView(scene)
		#print(ScenarioData.sc.getRoomBackLoc(0))
		#print(ScenarioData.sc.getObjectImgLoc(0, 0))
		
		pixmap = QtGui.QPixmap(self.scenarioData.getRoomBackLoc(0)).scaled(790, 534, QtCore.Qt.KeepAspectRatio)
		scene.addPixmap(pixmap)
		
		left_frame_layout.addWidget(view)

		# Settings
		right_frame = QtGui.QGroupBox("Asetukset")
		right_frame_layout = QtGui.QVBoxLayout()
		right_frame.setLayout(right_frame_layout)
		layout.addWidget(right_frame)
		
		settingsWidget = SettingsWidget(self)
		right_frame_layout.addWidget(settingsWidget)
		
	# Click on a room in the main tab
	def roomClicked(self, widgetItem):
		roomItems = widgetItem.room.getItems()
		self.drawRoomItems(roomItems)
		self.settingsWidget.setRoomOptions(widgetItem.room)
		
	# Click on an item in thre main tab room preview
	def roomItemClicked(self, widgetItem):
		self.settingsWidget.setItemOptions(widgetItem.item)
		
	# Draw the leftmost frame rooms
	def drawRooms(self):
		for i in range(len(self.scenarioData.roomList)):
			room = self.scenarioData.roomList[i]
			widgetItem = RoomWidget(room, self.scenarioData.dataDir)
			
			self.left_scene.addItem(widgetItem)
			
	# Draw the middle frame room items
	def drawRoomItems(self, roomItems):
		self.middle_scene.clear()
		for item in roomItems:
			# TODO: Resolve handling text objects (issue #8)
			if (item.getClassname() == "Text"):
				continue
				
			widgetItem = ItemWidget(item, self.scenarioData.dataDir)
			
			self.middle_scene.addItem(widgetItem)
			
	def getImageDir(self):
		return self.scenarioData.dataDir
		
	# Get View.Room objects
	def getRoomObjects(self):
		return self.scenarioData.getRooms()
		
	# Get given types of objects found in rooms
	def getObjectsByType(self, objectType):
		return self.scenarioData.getObjectsByType(objectType)
		
	# Get the target object that is triggered by the given item
	def getItemUse(self, item):
		return item.getUse()
		
# Room image with caption used in the main view
class RoomWidget(QtGui.QListWidgetItem):
	def __init__(self, room, imageDir, parent=None):
		super(RoomWidget, self).__init__(parent)
		
		self.room = room
		
		roomName = room.getName()
		if not (roomName):
			roomName = "Huoneella ei ole nimeä"
		self.setText(roomName)
		
		imagePath = imageDir+"/"+room.getBackground().getLocation()
		icon = QtGui.QIcon(imagePath)
		self.setIcon(icon)
		
# Item widget that represents items in game rooms
class ItemWidget(QtGui.QListWidgetItem):
	def __init__(self, item, imageDir, parent=None):
		super(ItemWidget, self).__init__(parent)
		
		# Row size, especially height
		self.setSizeHint(QtCore.QSize(100,100))
		
		self.item = item
		imageObject = item.getRepresentingImage()
		
		itemName = imageObject.getName()
		if not (itemName):
			itemName = "Esineellä ei ole nimeä"
		self.setText(itemName)
		
		imagePath = imageDir+"/"+imageObject.getLocation()
		icon = QtGui.QIcon(imagePath)
		self.setIcon(icon)
		
# Item and room settings widget
class SettingsWidget(QtGui.QWidget):
	def __init__(self, parent=None):
		super(SettingsWidget, self).__init__(parent)
		
		self.currentObject = None
		self.useTypes = {0: "Ei käyttöä", 1: "Käytä toiseen esineeseen",
			2: "Avaa jotakin", 3: "Laita johonkin", 4: "Poista este"}
			
		# Own widgets for object and room options
		self.objectLayout = QtGui.QGridLayout()
		self.objectWidget = QtGui.QWidget()
		self.objectWidget.setLayout(self.objectLayout)
		
		self.roomLayout = QtGui.QGridLayout()
		self.roomWidget = QtGui.QWidget()
		self.roomWidget.setLayout(self.roomLayout)
		
		layout = QtGui.QGridLayout()
		self.setLayout(layout)
		layout.addWidget(self.objectWidget)
		layout.addWidget(self.roomWidget)
		
		self.setSizePolicy(QtGui.QSizePolicy(
		QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed))
		
		self.parent = parent
		
		# Game item input fields
		self.objectNameEdit =  QtGui.QLineEdit()
		
		self.itemImage = QtGui.QLabel(self)
		self.itemImage.mousePressEvent = lambda s: self.showImageDialog(self.setRoomBackground)
		
		self.clickTextEdit = QtGui.QTextEdit()
		self.clickTextEdit.setMaximumHeight(50)
		
		self.pickupTextEdit = QtGui.QTextEdit()
		self.pickupTextEdit.setMaximumHeight(50)
		
		self.pickupBlockCombo = QtGui.QComboBox(self)
		self.pickupBlockCombo.setIconSize(QtCore.QSize(50,50))
		
		self.useTypeCombo = QtGui.QComboBox(self)
		
		# TODO: This combobox should be taller with the item chosen
		self.useTargetCombo = QtGui.QComboBox(self)
		self.useTargetCombo.setIconSize(QtCore.QSize(50,50))
		self.useTargetCombo.currentIndexChanged.connect(self.setUseTarget)
		
		self.useTextEdit = QtGui.QTextEdit()
		self.useTextEdit.setMaximumHeight(50)
		
		# Room options input fields
		self.roomNameEdit = QtGui.QLineEdit()
		
		self.musicTextEdit = QtGui.QLineEdit()
		self.musicTextEdit.setReadOnly(True)
		
		self.roomBackground = QtGui.QLabel(self)
		self.roomBackground.mousePressEvent = lambda s: self.showImageDialog(self.setRoomBackground)
		
		self.whereFromCombo = QtGui.QComboBox(self)
		self.whereFromCombo.setIconSize(QtCore.QSize(50,50))
		
		self.createItemOptions()
		self.createRoomOptions()
		
	#Settings for the object view
	#TODO: Reduce redundancy; similar settings layout, "Name", "Picture" etc., are defined many times
	def createItemOptions(self):
		nameLabel = QtGui.QLabel("Nimi")
		
		# Object image
		imgTextLabel = QtGui.QLabel("Kuva")
		
		clickTextLabel = QtGui.QLabel("Teksti klikatessa:")
		
		# Pickup text section
		pickupLabel = QtGui.QLabel("Poiminta")
		pickupLabelLine = QtGui.QLabel("")
		pickupLabelLine.setFrameStyle(QtGui.QFrame.HLine | QtGui.QFrame.Raised)
		
		pickupTextLabel = QtGui.QLabel("Teksti poimittaessa:")
		
		pickupBlockLabel = QtGui.QLabel("Estääkö jokin poiminnan?")
		self.populateBlockingCombobox()
		
		# Object usage
		useLabel = QtGui.QLabel("Käyttö")
		useLabelLine = QtGui.QLabel("")
		useLabelLine.setFrameStyle(QtGui.QFrame.HLine | QtGui.QFrame.Raised)
		
		# Object type of usage
		for i in self.useTypes:
			self.useTypeCombo.addItem(self.useTypes[i])
		self.useTypeCombo.currentIndexChanged.connect(self.changeUseType)
			
		self.populateUseTargetCombobox(0)
		
		useTextLabel = QtGui.QLabel("Teksti käytettäessä:")
		
		allTextsButton = QtGui.QPushButton("Nämä ja muut tekstit")
		allTextsButton.clicked.connect(self.showAllTexts)
		
		self.objectLayout.addWidget(nameLabel, 0, 0)
		self.objectLayout.addWidget(self.objectNameEdit, 0, 1, 1, 2)
		self.objectLayout.addWidget(imgTextLabel, 1, 0)
		self.objectLayout.addWidget(self.itemImage, 1, 1, 2, 2)
		self.objectLayout.addWidget(clickTextLabel, 4, 0)
		self.objectLayout.addWidget(self.clickTextEdit, 4, 1)
		self.objectLayout.addWidget(pickupLabelLine, 5, 0, 1, 2)
		self.objectLayout.addWidget(pickupLabel, 6, 0)
		self.objectLayout.addWidget(pickupTextLabel, 7, 0)
		self.objectLayout.addWidget(self.pickupTextEdit, 7, 1)
		self.objectLayout.addWidget(pickupBlockLabel, 8, 0)
		self.objectLayout.addWidget(self.pickupBlockCombo, 8, 1)
		self.objectLayout.addWidget(useLabelLine, 9, 0, 1, 2)
		self.objectLayout.addWidget(useLabel, 10, 0)
		self.objectLayout.addWidget(self.useTypeCombo, 11, 1)
		self.objectLayout.addWidget(self.useTargetCombo, 12, 1)
		self.objectLayout.addWidget(useTextLabel, 13, 0)
		self.objectLayout.addWidget(self.useTextEdit, 13, 1)
		self.objectLayout.addWidget(allTextsButton, 14, 1)
	
	# Create the input fields for object options
	def setItemOptions(self, item):
		self.roomWidget.hide()
		self.objectWidget.show()
		
		self.currentObject = item
		imageObject = item.getRepresentingImage()
		
		# Object name
		itemName = imageObject.getName()
		if not (itemName):
			itemName = "Esineellä ei ole nimeä"
		self.objectNameEdit.setText(itemName)
		
		# Item background
		self.setItemImage(self.parent.getImageDir()+"/"+imageObject.getLocation())
		
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
		print("HERE")
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
		print("typoa", useType, itemTarget)
		# Use text
		useText = item.getUseText()
		if not (useText):
			useText = ""
		self.useTextEdit.setText(useText)
		
	# Create the input fields for game rooms
	def createRoomOptions(self):
		#TODO: Change room attributes in real time or after closing the dialog?
		# TODO: Align the layout to the top
		nameLabel = QtGui.QLabel("Nimi")
		
		# Room image
		imgTextLabel = QtGui.QLabel("Kuva")
		
		# Music
		# TODO: How to clear music?
		musicLabel = QtGui.QLabel("Musiikki")
		musicBtn = QtGui.QPushButton('Selaa...', self)
		musicBtn.setToolTip('Valitse musiikkitiedosto')
		musicBtn.resize(musicBtn.sizeHint())
		musicBtn.clicked.connect(self.showMusicDialog)
		
		# Where from dropdown box
		whereFromLabel = QtGui.QLabel("Mistä sinne pääsee?")
		self.populateRoomCombobox()
		
		self.roomLayout.addWidget(nameLabel, 0, 0)
		self.roomLayout.addWidget(self.roomNameEdit, 0, 1, 1, 2)
		self.roomLayout.addWidget(imgTextLabel, 1, 0)
		self.roomLayout.addWidget(self.roomBackground, 1, 1, 2, 2)
		self.roomLayout.addWidget(musicLabel, 4, 0)
		self.roomLayout.addWidget(self.musicTextEdit, 4, 1)
		self.roomLayout.addWidget(musicBtn, 4, 2)
		self.roomLayout.addWidget(whereFromLabel, 6, 0)
		self.roomLayout.addWidget(self.whereFromCombo, 6, 1, 1, 2)
	
	# Set settings for the room view
	def setRoomOptions(self, room):
		self.objectWidget.hide()
		self.roomWidget.show()
		
		self.currentObject = room
		
		# Room name
		roomName = room.getName()
		if not (roomName):
			roomName = "Huoneella ei ole nimeä"
		self.roomNameEdit.setText(roomName)
		
		# Room background
		self.setRoomBackground(self.parent.getImageDir()+"/"+room.getBackground().getLocation())
		
		# Room music may return None which doesn't have split
		try:
			roomMusic = room.getMusic().split("/")[-1]
		except AttributeError:
			roomMusic = ""
		self.musicTextEdit.setText(roomMusic)
		
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
		
	def setRoomBackground(self, imagePath):
		imgPixmap = QtGui.QPixmap(imagePath).scaled(200, 200, QtCore.Qt.KeepAspectRatio)
		self.roomBackground.setPixmap(imgPixmap)
		
	def setItemImage(self, imagePath):
		imgPixmap = QtGui.QPixmap(imagePath)
		# TODO: Have spacing for smaller items
		if (imgPixmap.size().height() > 200):
			imgPixmap = imgPixmap.scaled(200, 200, QtCore.Qt.KeepAspectRatio)
		self.itemImage.setPixmap(imgPixmap)
		
	# TODO: Maybe have doors here instead of rooms (categorized by rooms maybe)
	# TODO: Need to set this box value in settings
	def populateRoomCombobox(self):
		for room in self.parent.getRoomObjects():
			# TODO: Some model to eliminate redundancy of this kind of getName/roomName patterns
			roomName = room.getName()
			if not (roomName):
				roomName = "Huoneella ei ole nimeä"
			imgPixmap = QtGui.QPixmap(self.parent.getImageDir()+"/"+room.getBackground().getLocation())
			
			roomIcon = QtGui.QIcon(imgPixmap)
			self.whereFromCombo.addItem(roomIcon, roomName)
			
	# TODO: Implement me properly
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
					
if __name__ == '__main__':
	from sys import argv, exit

	app = QtGui.QApplication(argv)

	editor = Editor()
	editor.show()
	exit(app.exec_())
