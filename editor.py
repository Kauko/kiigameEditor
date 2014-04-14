# -*- coding: UTF-8 -*-

from PySide import QtGui, QtCore
import SettingsWidget, ScenarioData
from ImageCache import ImageCache
from os.path import dirname, abspath
import ModuleLocation

# TODO: Keeping mouse down and moving it around in item combo shows items
#		one step behind

class Editor(QtGui.QMainWindow):
	def __init__(self, parent=None):
		super(Editor, self).__init__(parent)
		
		self.editorImagePath = "%s/images/" %(dirname(abspath(ModuleLocation.getLocation())))
		self.scenarioData = ScenarioData.ScenarioData("latkazombit")
		self.scenarioData.loadScenario()
		
		self.imageCache = ImageCache()
		
		self.placeholderImages = {
			"Room": "room_placeholder.png",
			"Sequence": "sequence_placeholder.png",
			"Sequenceimage": "sequence_placeholder.png",
			"Object": "object_placeholder.png",
			"Item": "object_placeholder.png",
			"Door": "door_placeholder.png",
			"Container": "container_placeholder.png",
			"Obstacle": "obstacle_placeholder.png",
			"Text": "text_placeholder.png"
		}
		self.newIconPath = self.editorImagePath + "add_new_icon.png"
		self.noChoiceIconPath = self.editorImagePath + "no_choice_icon.png"
		
		self.setWindowTitle("Kiigame - Pelieditori")
		
		self.tabWidget = QtGui.QTabWidget()
		self.setCentralWidget(self.tabWidget)
		
		self.createMenuActions()
		self.createMenus()
		self.createMainTab()
		self.createSpaceTab()
		self.createTextsTab()
		
		self.tabWidget.addTab(self.mainTab, "Päänäkymä")
		self.tabWidget.addTab(self.spaceTab, "Tila")
		self.tabWidget.addTab(self.textsTab, "Tekstit")
		self.tabWidget.currentChanged.connect(self.onTabChanged)
		
	def createMenuActions(self):
		self.newAct = QtGui.QAction("Uusi", self)
		self.openAct = QtGui.QAction("Avaa…", self)
		self.saveAct = QtGui.QAction("Tallenna", self)
		self.saveAct.triggered.connect(self.scenarioData.saveScenario)
		self.exitAct = QtGui.QAction("Lopeta", self)
		#TODO: Nice-to-have, ask for confirmation before quitting?
		self.exitAct.triggered.connect(self.close)
	
	def createMenus(self):
		fileMenu = self.menuBar().addMenu("&Tiedosto")
		fileMenu.addAction(self.newAct)
		fileMenu.addAction(self.openAct)
		fileMenu.addAction(self.saveAct)
		fileMenu.addSeparator()
		fileMenu.addAction(self.exitAct)
		
	def createMainTab(self):
		self.mainTab = QtGui.QWidget()
		
		self.mainLayout = QtGui.QGridLayout()
		self.mainTab.setLayout(self.mainLayout)
		
		# Room preview
		left_frame = QtGui.QGroupBox("Tilat")
		left_frame_layout = QtGui.QGridLayout()
		left_frame.setLayout(left_frame_layout)
		self.mainLayout.addWidget(left_frame, 1, 0, 1, 2)
		
		# Set-up widget for showing rooms
		self.left_scene = QtGui.QListWidget(self)
		self.left_scene.setIconSize(QtCore.QSize(200, 200))
		self.left_scene.setViewMode(QtGui.QListView.IconMode)
		self.left_scene.setFlow(QtGui.QListView.LeftToRight)
		self.left_scene.setMovement(QtGui.QListView.Static)
		self.left_scene.itemSelectionChanged.connect(self.roomClicked)
		self.left_scene.doubleClicked.connect(self.comboDoubleClicked)
		self.left_scene.clicked.connect(self.roomClicked)
		left_frame_layout.addWidget(self.left_scene)
		
		self.addViewsCombo = QtGui.QComboBox(self)
		self.addViewsCombo.addItem("Lisää tila")
		self.addViewsCombo.addItem("Huone", userData="room")
		self.addViewsCombo.addItem("Välianimaatio", userData="sequence")
		#self.addViewsCombo.addItem("Loppukuva", userData="end")
		self.addViewsCombo.currentIndexChanged.connect(self.addViewsComboChanged)
		self.mainLayout.addWidget(self.addViewsCombo, 0, 0)
		
		# Draw rooms and select the first one
		self.drawRooms()
		selectedRoom = self.left_scene.itemAt(0, 0)
		self.left_scene.setCurrentItem(selectedRoom)
		
		# Room items
		middle_frame = QtGui.QGroupBox("Tilan objektit")
		middle_frame_layout = QtGui.QVBoxLayout()
		middle_frame.setLayout(middle_frame_layout)
		self.mainLayout.addWidget(middle_frame, 1, 2, 1, 2)
		
		# Settings for items and rooms
		right_frame = QtGui.QGroupBox("Asetukset")
		self.right_frame_layout_main = QtGui.QVBoxLayout()
		right_frame.setLayout(self.right_frame_layout_main)
		self.mainLayout.addWidget(right_frame, 1, 4)
		
		self.settingsWidget = SettingsWidget.SettingsWidget(self)
		self.settingsWidget.displayOptions(selectedRoom.room)
		
		# Set settings widget scrollable instead resizing main window
		self.scrollAreaMain = QtGui.QScrollArea()
		self.scrollAreaMain.setWidgetResizable(True)
		self.right_frame_layout_main.addWidget(self.scrollAreaMain)
		self.scrollAreaMain.setWidget(self.settingsWidget)
		
		# Set-up widget for showing room items
		self.middle_scene = QtGui.QListWidget(self)
		self.middle_scene.setIconSize(QtCore.QSize(100, 100))
		self.middle_scene.setMovement(QtGui.QListView.Static)
		self.middle_scene.itemSelectionChanged.connect(self.roomItemClicked)
		middle_frame_layout.addWidget(self.middle_scene)
		self.middle_scene.doubleClicked.connect(self.comboDoubleClicked)
		
		self.addObjectsCombo = QtGui.QComboBox(self)
		self.mainLayout.addWidget(self.addObjectsCombo, 0, 2)
		self.addObjectsCombo.currentIndexChanged.connect(self.addObjectsComboChanged)
		self.populateAddObjectsCombo()
		
		# Adding buttons for removing views and objects
		self.removeViewsButton = QtGui.QPushButton("Poista valittu tila")
		self.setRemoveViewsButtonDisabled()
		self.removeViewsButton.clicked.connect(self.removeViewsButtonClicked)
		self.mainLayout.addWidget(self.removeViewsButton, 0, 1)
		
		self.removeObjectsButton = QtGui.QPushButton("Poista valittu esine")
		self.setRemoveObjectsButtonDisabled()
		self.removeObjectsButton.clicked.connect(self.removeObjectsButtonClicked)
		self.mainLayout.addWidget(self.removeObjectsButton, 0, 3)
		
		self.drawRoomItems()
		
	def comboDoubleClicked(self):
		self.tabWidget.setCurrentIndex(1)
		
	def populateAddObjectsCombo(self):
		selectedType = self.left_scene.currentItem().room.__class__.__name__
		
		# Disable adding objects in the start view
		if (selectedType in ("Start", "End")):
			self.addObjectsCombo.setDisabled(True)
			self.setRemoveObjectsButtonDisabled(forceDisable=True)
			return
			
		self.addObjectsCombo.setDisabled(False)
		self.addObjectsCombo.clear()
		self.addObjectsCombo.addItem("Lisää esine valittuun tilaan")
		
		if (selectedType == "Room"):
			self.addObjectsCombo.addItem("Kiinteä esine", userData="object")
			self.addObjectsCombo.addItem("Käyttöesine", userData="item")
			self.addObjectsCombo.addItem("Ovi", userData="door")
			self.addObjectsCombo.addItem("Säiliö", userData="container")
			self.addObjectsCombo.addItem("Este", userData="obstacle")
		elif (selectedType == "Sequence"):
			self.addObjectsCombo.addItem("Kuva", userData="sequenceimage")
			
	def getPlaceholderImagePath(self, objectType):
		return self.editorImagePath + self.placeholderImages[objectType.capitalize()]
		
	def addViewsComboChanged(self):
		selected = self.addViewsCombo.itemData(self.addViewsCombo.currentIndex())
		if not (selected in ("room", "sequence", "end")):
			return
		self.createView(selected)
		
	def removeViewsButtonClicked(self):
		# Remove from game data
		selected = self.left_scene.currentItem()
		self.scenarioData.removeView(selected.room)
		
		# Remove from combobox
		row = self.left_scene.currentRow()
		self.left_scene.takeItem(row)
		
		self.drawRoomItems()
		
	def addObjectsComboChanged(self):
		selected = self.addObjectsCombo.itemData(self.addObjectsCombo.currentIndex())
		if not (selected in ("object", "item", "door", "container", "obstacle", "sequenceimage")):
			return
		self.createObject(selected)
	
	def roomsComboboxChanged(self):
		selectedRoom = self.roomsCombobox.itemData(self.roomsCombobox.currentIndex())
		selectedItem = self.settingsWidget.currentObject
		for room in self.getRoomObjects():
			if room == selectedRoom:
				room.moveItem(selectedItem)
		self.left_scene.selectedItems()[0].room.removeObject(selectedItem)
		self.updateSpaceTab()
		
	def removeObjectsButtonClicked(self):
		# Remove from the room
		selected = self.settingsWidget.currentObject
		selected.parentView.removeObject(selected)
		self.updateSpaceTab()
		
		# Update items combobox
		self.drawRoomItems()
		
	def setRemoveObjectsButtonDisabled(self, forceDisable=False):
		selected = self.settingsWidget.currentObject
		objectType = selected.__class__.__name__
		if (objectType == "Room" or objectType == "Sequence" or objectType == "SequenceImage" or objectType == "Start" or
			objectType == "End" or objectType == "Text" or objectType == "JSONImage" or objectType == "MenuImage" or objectType == "BeginingImage"):
			isDisabled = True
		else:
			isDisabled = False
			
		self.removeObjectsButton.setDisabled(isDisabled)
		
	def setRemoveViewsButtonDisabled(self, forceDisable=False):
		selected = self.settingsWidget.currentObject
		objectType = selected.__class__.__name__
		if (objectType == "Room" or objectType == "Sequence" or objectType == "SequenceImage" or objectType == "Start" or
			objectType == "End" or objectType == "MenuImage" or objectType == "BeginingImage"):
			isDisabled = False
		else:
			isDisabled = True
			
		self.removeViewsButton.setDisabled(isDisabled)
		
	def createSpaceTab(self):
		self.spaceTab = QtGui.QWidget()

		self.spaceLayout = QtGui.QGridLayout()
		self.spaceTab.setLayout(self.spaceLayout)
		
		# Another settings widget for room view
		#self.spaceSettingsWidget = SettingsWidget.SettingsWidget(self)
		selectedRoom = self.left_scene.selectedItems()[0]
		self.settingsWidget.displayOptions(selectedRoom.room)

		# Room
		left_frame = QtGui.QGroupBox("Tila")
		left_frame_layout = QtGui.QHBoxLayout()
		left_frame.setLayout(left_frame_layout)
		self.spaceLayout.addWidget(left_frame, 1, 0, 1, 6)

		# Settings
		right_frame = QtGui.QGroupBox("Asetukset")
		self.right_frame_layout_space = QtGui.QVBoxLayout()
		right_frame.setLayout(self.right_frame_layout_space)
		self.spaceLayout.addWidget(right_frame, 1, 6, 1, 1)
		
		self.scrollAreaSpace = QtGui.QScrollArea()
		self.scrollAreaSpace.setWidgetResizable(True)
		self.right_frame_layout_space.addWidget(self.scrollAreaSpace)
		
		self.spaceScene = QtGui.QGraphicsScene(self)
		self.spaceView = QtGui.QGraphicsView(self.spaceScene)
		left_frame_layout.addWidget(self.spaceView)
		
		# Z-index buttons
		zIndexLabel = QtGui.QLabel("Järjestys:")
		increaseButton = QtGui.QPushButton("Tuo esine eteen")
		increaseButton.clicked.connect(lambda: self.changeItemZIndex(1, self.settingsWidget.currentObject))
		decreaseButton = QtGui.QPushButton("Vie esine taakse")
		decreaseButton.clicked.connect(lambda: self.changeItemZIndex(-1, self.settingsWidget.currentObject))
		#left_frame_layout.addWidget(zIndexLabel, 1, 9)
		
		# Combobox for putting item into another room
		self.roomsCombobox = QtGui.QComboBox(self)
		self.roomsCombobox.setIconSize(QtCore.QSize(20,20))
		for room in self.getRoomObjects():
			roomName = room.getName()
			if not (roomName):
				roomName = "%s ei ole nimeä" %(room.generalNameAdessive)
			imgPixmap = self.imageCache.createPixmap(room.getRepresentingImage().getRepresentingImage().absoluteImagePath)
			roomIcon = QtGui.QIcon(imgPixmap)
			self.roomsCombobox.addItem(roomIcon, roomName, userData=room)
		self.roomsCombobox.currentIndexChanged.connect(self.roomsComboboxChanged)
		
		changeRooms = QtGui.QLabel("Siirrä esine eri huoneeseen:")
		
		# Buttons bar
		self.spaceLayout.addWidget(zIndexLabel, 0, 2)
		self.spaceLayout.addWidget(increaseButton, 0, 3)
		self.spaceLayout.addWidget(decreaseButton, 0, 4)
		self.spaceLayout.addWidget(changeRooms, 0, 5)
		self.spaceLayout.addWidget(self.roomsCombobox, 0, 6)
		
		self.updateSpaceTab()
		
	def drop(self, event):
		print("drop!")
		
	def updateSpaceTab(self):
		selectedRoom = self.left_scene.selectedItems()[0]
		#self.settingsWidget.displayOptions(selectedRoom.room)
		self.spaceScene.clear()
		
		# Display room image and set the same scale than in the game
		pixmap = self.imageCache.createPixmap(selectedRoom.room.getRepresentingImage().absoluteImagePath).scaled(981, 543)
		pixmapWidget = QtGui.QLabel()
		pixmapWidget.setPixmap(pixmap)
		pixmapWidget.setGeometry(0, 200, pixmap.width(), pixmap.height())
		self.spaceScene.addPixmap(pixmap)
		self.spaceItems = selectedRoom.room.getItems()
		
		# Display objects
		for item in self.spaceItems:
			# TODO: Resolve handling text objects (issue #8)
			#if (item.getClassname() == "Text"):
			#	continue
			
			img = item.getRepresentingImage()
			if (item.getClassname() == "Text"):
				continue
			#print(self.scenarioData.dataDir + "/" + img.getSource())
			
			try:
				scale = img.imageAttributes["scale"]
			except:
				scale = 1
			
			pixmap = self.imageCache.createPixmap(img.absoluteImagePath)
			pixmap = pixmap.scaledToHeight(pixmap.height()*scale)
			pixItem = SpaceViewItem(pixmap, item.id, self)
			pixItem.setFlag(QtGui.QGraphicsItem.ItemIsMovable)
			pixItem.setFlag(QtGui.QGraphicsItem.ItemIsSelectable)
			pixItem.setFlag(QtGui.QGraphicsItem.ItemSendsGeometryChanges)
			pixItem.setAcceptDrops(True)
			
			inEmptyRoom = False

			pos = item.getPosition()
			if not (pos):
				inEmptyRoom = True
			
			if(inEmptyRoom):
				print("In empty room")
			else:
				pixItem.setPos(pos[0],pos[1])
				self.spaceScene.addItem(pixItem)
				
		selectedRoom.room.setItems(self.spaceItems)

	def changeItemZIndex(self, change, item):
		if not (item in self.spaceItems):
			return
	
		index = self.spaceItems.index(item)
		if (change == -1):
			if (index != 0):
				self.spaceItems.insert(index-1, self.spaceItems.pop(index))
		elif (change == 1):
			if (index != len(self.spaceItems)-1):
				self.spaceItems.insert(index+1, self.spaceItems.pop(index))

		self.updateSpaceTab()

	def onTabChanged(self, index):
		# Main tab
		if (index == 0):
			#self.right_frame_layout_main.addWidget(self.scrollAreaMain)
			self.scrollAreaMain.takeWidget()
			self.scrollAreaMain.setWidget(self.settingsWidget)
			self.mainLayout.addWidget(self.addObjectsCombo, 0, 2)
			self.mainLayout.addWidget(self.removeObjectsButton, 0, 3)
			self.setRemoveObjectsButtonDisabled()
		# Space tab
		elif (index == 1):
			#self.right_frame_layout_space.addWidget(self.scrollAreaSpace)
			self.scrollAreaSpace.takeWidget()
			self.scrollAreaSpace.setWidget(self.settingsWidget)
			self.spaceLayout.addWidget(self.addObjectsCombo, 0, 0)
			self.spaceLayout.addWidget(self.removeObjectsButton, 0, 1)
			self.setRemoveObjectsButtonDisabled()
		# Texts tab
		elif (index == 2):
			self.drawTextItems
			
	def createObject(self, objectType):
		selectedRoom = self.left_scene.selectedItems()[0]
		
		if (objectType == "object"):
			newObject = selectedRoom.room.addObject()
		elif (objectType == "item"):
			newObject = selectedRoom.room.addItem()
		elif (objectType == "door"):
			newObject = selectedRoom.room.addDoor()
		elif (objectType == "container"):
			newObject = selectedRoom.room.addContainer()
		elif (objectType == "obstacle"):
			newObject = selectedRoom.room.addObstacle()
		elif (objectType == "sequenceimage"):
			newObject = selectedRoom.room.addImage()
		else:
			return
			
		placeholderImage = self.getPlaceholderImagePath(objectType)
		
		# Set placeholder image source
		newObject.getRepresentingImage().placeholderImage.setSource(placeholderImage)
		
		# Create new combobox item
		itemWidget = ItemWidget(newObject)
		self.middle_scene.addItem(itemWidget)
		
		# Focus on the new item
		self.addObjectsCombo.setCurrentIndex(0)
		self.middle_scene.setCurrentRow(self.middle_scene.count()-1)
		self.drawTextItems()
		
		# Update settingsWidget comboboxes
		self.settingsWidget.updateComboboxes(objectType)
		
	def createView(self, objectType):
		
		# Create the new view and the placeholder image
		if (objectType == "room"):
			newObject = self.scenarioData.addRoom(None, None, None)
		elif (objectType == "sequence"):
			newObject = self.scenarioData.addSequence(None, None, None)
		else:
			return
			
		newObject.createPlaceholderImage(self.getPlaceholderImagePath(objectType))
		
		# Create combobox item
		widgetItem = ViewWidget(newObject, self.scenarioData.dataDir)
		self.left_scene.addItem(widgetItem)
		
		# Focus on the created image
		self.addObjectsCombo.setCurrentIndex(0)
		self.left_scene.setCurrentRow(self.left_scene.count()-1)
		
		# Update settingsWidget comboboxes
		self.settingsWidget.updateComboboxes(objectType)
		
	def createTextsTab(self):
		self.textsTab = QtGui.QWidget()

		layout = QtGui.QHBoxLayout()
		self.textsTab.setLayout(layout)

		# Objects
		left_frame = QtGui.QGroupBox("Esineet")
		left_frame_layout = QtGui.QVBoxLayout()
		left_frame.setLayout(left_frame_layout)
		layout.addWidget(left_frame)
		
		# Set-up widget for showing room items
		self.text_scene = QtGui.QTableWidget(self)
		#text_scene.setMovement(QtGui.QListView.Static)
		self.text_scene.itemSelectionChanged.connect(self.textItemClicked)
		
		left_frame_layout.addWidget(self.text_scene)
		
		# Draw all items and their progress bar
		self.drawTextItems()
		
		# Select the first item
		selectedItem = self.text_scene.itemAt(0, 0)
		self.text_scene.setCurrentItem(selectedItem)
		
		# Texts
		self.texts_frame = QtGui.QGroupBox("Tekstit - %s" %(selectedItem.text()))
		self.texts_frame_layout = QtGui.QVBoxLayout()
		self.texts_frame.setLayout(self.texts_frame_layout)
		layout.addWidget(self.texts_frame)
		
		self.textsWidget = TextsWidget(self.scenarioData, self)
		self.texts_frame_layout.addWidget(self.textsWidget)
		
		self.textsWidget.displayTexts(selectedItem)
		
	# Click on an object in the texts tab object list
	def textItemClicked(self):
		selected = self.text_scene.currentItem()
		if (selected):
			# TODO: Handle this better? Now there's a warning at the
			# beginning that textsWidget doesn't exist
			self.textsWidget.displayTexts(selected)
			self.texts_frame.setTitle("Tekstit - %s" %(selected.text()))
		
	def drawTextItems(self):
		#print ("DRAWING")
		textItems = self.scenarioData.getAllObjects()
		secretCount = textItems.pop()
		imgCount = textItems.pop()
		textItems = textItems.pop()
		
		self.text_scene.setRowCount(0)
		self.text_scene.setColumnCount(2)
		self.text_scene.setColumnWidth(0, 250)
		self.text_scene.setColumnWidth(1, 200)
		
		# Disable sorting for row count, enable it after adding items
		self.text_scene.setSortingEnabled(False)
		row = 0
		for item in textItems:
			for itemImage in item.getImages():
				textCount = len(itemImage.texts)
				
				# Add a row
				self.text_scene.insertRow(self.text_scene.rowCount())
				
				# Add a text item to the first column
				widgetItem = TextItemWidget(itemImage, item, self.scenarioData.dataDir, 25)
				self.text_scene.setItem(row, 0, widgetItem)
				
				# Maximum amount of texts for item
				maxAmount = 0
				if ("examine" in itemImage.texts):
					maxAmount += 1
					if (itemImage.texts["examine"] == ""):
						textCount -= 1
					
				if ("pickup" in itemImage.texts):
					maxAmount += 1
				# TODO: Sorting doesn't work, fix possibly by setItem here and setCellWidget inside item
				if ("name" in itemImage.texts):
					textCount -= 1
					
				if (itemImage.imageAttributes["category"] == "secret"):
					maxAmount = 1
					
				if (item.__class__.__name__ == "Item"
					or itemImage.imageAttributes["category"] == "reward"):
					# Max amount is number of all images minus item itself and secrets (no interaction)
					maxAmount += imgCount-1-secretCount
					
					# Different pictures for the inventory and the room
					if ("src2" in itemImage.imageAttributes or itemImage.imageAttributes["category"] == "secret"):
						maxAmount = 1
					
				# Add a progressbar to the second column
				#progressBarItem = ProgressBarItemWidget(item, maxAmount)
				#print (item.id, textCount, maxAmount)
				#if (textCount == 0):
				#	print ("HERE", len(item.texts), item.id, itemImage.texts)
				progressBar = QtGui.QProgressBar()
				progressBar.setMinimum(0)
				progressBar.setMaximum(maxAmount)
				progressBar.setValue(textCount)
				
				self.text_scene.setCellWidget(row, 1, progressBar)
				
				row += 1
		self.text_scene.setSortingEnabled(True)
	
	# Click on a room in the main tab
	def roomClicked(self):
		self.drawRoomItems()
		self.settingsWidget.displayOptions(self.left_scene.selectedItems()[0].room)
		self.setRemoveViewsButtonDisabled()
		self.populateAddObjectsCombo()
		self.setRemoveObjectsButtonDisabled()
		self.updateSpaceTab()
		
	# Click on an item in the main tab room preview
	def roomItemClicked(self):
		# TODO: Clear when suitable (like when no items in the view)
		selected = self.middle_scene.currentItem()
		if (selected):
			self.settingsWidget.displayOptions(selected.item)
		
		self.setRemoveViewsButtonDisabled()
		self.setRemoveObjectsButtonDisabled()
		
	# Draw the leftmost frame items
	def drawRooms(self):
		self.left_scene.clear()
		
		# Rooms
		for i in range(len(self.scenarioData.roomList)):
			room = self.scenarioData.roomList[i]
			widgetItem = ViewWidget(room, self.scenarioData.dataDir)
			
			self.left_scene.addItem(widgetItem)
			
		# TODO: Draw sequence images in order, allow reordering them with mouse
		# Sequences
		for i in range(len(self.scenarioData.sequenceList)):
			sequence = self.scenarioData.sequenceList[i]
			widgetItem = ViewWidget(sequence, self.scenarioData.dataDir)
			
			self.left_scene.addItem(widgetItem)
			
		# Ends
		for i in range(len(self.scenarioData.endViewList)):
			end = self.scenarioData.endViewList[i]
			widgetItem = ViewWidget(end, self.scenarioData.dataDir)
			
			self.left_scene.addItem(widgetItem)
			
		# Start
		widgetItem = ViewWidget(self.scenarioData.startView, self.scenarioData.dataDir)
		self.left_scene.addItem(widgetItem)
			
	# Draw the middle frame room items
	def drawRoomItems(self):
		self.middle_scene.clear()
		
		# There might not be a selection in left_scene
		try:
			roomItems = self.left_scene.currentItem().room.getItems()
		except IndexError:
			return
			
		for item in roomItems:
			imagePath = None
			if (item.__class__.__name__ == "Text"):
				imagePath = self.getPlaceholderImagePath("Text")
			widgetItem = ItemWidget(item, imagePath)
			
			self.middle_scene.addItem(widgetItem)
			
	def getImageDir(self):
		return self.scenarioData.dataDir
		
	def getRoomObjects(self):
		return self.scenarioData.getRooms()
		
	# Get given types of objects found in rooms
	def getObjectsByType(self, objectType):
		return self.scenarioData.getObjectsByType(objectType)
		
	# Get the target object that is triggered by the given item
	def getItemUse(self, item):
		return item.getUse()
		
	# Get the general object name for an object type
	def getGeneralName(self, objectType):
		return self.scenarioData.getGeneralName(objectType)
		
# Widget used to display rooms, sequences, start and end views
class ViewWidget(QtGui.QListWidgetItem):
	def __init__(self, room, imageDir, parent=None):
		super(ViewWidget, self).__init__(parent)
		
		self.room = room
		
		if (room.nameable):
			roomName = room.getName()
			if not (roomName):
				roomName = "%s ei ole nimeä" %(room.generalNameAdessive)
		else:
			roomName = room.generalName
			
		self.setText(roomName)
		
		imagePath = room.getRepresentingImage().absoluteImagePath
		icon = QtGui.QIcon(imagePath)
		self.setIcon(icon)
		
# Item widget that represents items in game views
class ItemWidget(QtGui.QListWidgetItem):
	def __init__(self, item, imagePath=None, parent=None):
		super(ItemWidget, self).__init__(parent)
		
		# Row size, especially height
		self.setSizeHint(QtCore.QSize(100,100))
		
		self.item = item
		imageObject = item.getRepresentingImage().getRepresentingImage()
		
		itemName = imageObject.getName()
		if not (itemName):
			itemName = "%s ei ole nimeä" %(item.generalNameAdessive)
		self.setText(itemName)
		
		# imagePath can be overriden
		if not (imagePath):
			imagePath = imageObject.absoluteImagePath
			
		icon = QtGui.QIcon(imagePath)
		self.setIcon(icon)

# Text item widget that represents items in texts tab
class TextItemWidget(QtGui.QTableWidgetItem):
	def __init__(self, textItem, parentItem, imageDir, cellSize, parent=None):
		super(TextItemWidget, self).__init__(parent)
		
		# Row size, especially height
		self.setSizeHint(QtCore.QSize(cellSize, cellSize))
		
		self.id = textItem.id
		self.textItem = textItem
		self.parentItem = parentItem
		self.objectType = parentItem.__class__.__name__
		self.texts = textItem.texts
		
		if (self.textItem.imageAttributes["category"] == "reward"):
			self.objectType = "Item"
		
		try:
			self.target = parentItem.getUse().getName()
		except:
			self.target = None
		
		try:
			self.useText = parentItem.getUseText()
		except:
			self.useText = ""
		
		textItemName = self.textItem.getName()
		if not (textItemName):
			textItemName = "%s ei ole nimeä" %(self.textItem.generalNameAdessive)
		else:
			textItemName += self.getImageType()
		self.setText(textItemName)
		
		imagePath = imageDir+"/"+textItem.imageAttributes["src"]
		icon = QtGui.QIcon(imagePath)
		self.setIcon(icon)

	def getImageType(self):
		for attribute in dir(self.parentItem):
			if (self.textItem == getattr(self.parentItem, attribute)):
				if (attribute == "openImage"):
					return " - Auki"
				elif (attribute == "closedImage"):
					return " - Kiinni"
				elif (attribute == "lockedImage"):
					return " - Lukittu"
				elif (attribute == "emptyImage"):
					return " - Tyhjä"
				elif (attribute == "fullImage"):
					return " - Täysi"
				elif (attribute == "blockingImage"):
					return " - Estää"
				elif (attribute == "unblockingImage"):
					return " - Ei estä"
				elif (attribute == "blockedImage"):
					return " - Estetty"
		return ""

# ProgressBar item that shows how much item has texts completed
#class ProgressBarItemWidget(QtGui.QTableWidgetItem):
#	def __init__(self, textItem, maxAmount, parent=None):
#		super(ProgressBarItemWidget, self).__init__(parent)
#
#		self.progressBar = QtGui.QProgressBar()
#		self.textItem = textItem
#		self.maxAmount = maxAmount
#
#		self.calculateProgress()
#
#	def calculateProgress(self): # If there's many images, .texts doesn't work!
#
#		print ("LOL", self.textItem.id, self.maxAmount, len(self.textItem.texts)-1)
#		self.progressBar.setMinimum(0)
#		self.progressBar.setMaximum(self.maxAmount)
#		self.progressBar.setValue(len(self.textItem.texts)-1)

# Texts widget that shows texts of specific item in the texts tab
class TextsWidget(QtGui.QWidget):
	def __init__(self, scenarioData, parent=None):
		super(TextsWidget, self).__init__(parent)

		self.parent = parent
		self.scenarioData = scenarioData
		self.layout = QtGui.QGridLayout()
		self.setLayout(self.layout)
		
		# Examine
		self.clickTextLabel = QtGui.QLabel("Teksti klikatessa:")
		self.clickTextEdit = QtGui.QTextEdit()
		self.clickTextEdit.setMaximumHeight(50)
		self.clickTextEdit.focusOutEvent = lambda s: self.changeText("click")
		
		# Pickup text
		self.pickupTextLabel = QtGui.QLabel("Teksti poimiessa:")
		self.pickupTextEdit = QtGui.QTextEdit()
		self.pickupTextEdit.setMaximumHeight(50)
		self.pickupTextEdit.focusOutEvent = lambda s: self.changeText("pickup")
		
		# Use text
		self.useTextLabel = QtGui.QLabel("")
		self.useTextEdit = QtGui.QTextEdit()
		self.useTextEdit.setMaximumHeight(50)
		self.useTextEdit.focusOutEvent = lambda s: self.changeText("use")
		
		# Default text
		self.defaultTextLabel = QtGui.QLabel("Oletusteksti puuttuville teksteille:")
		self.defaultTextEdit = QtGui.QTextEdit()
		self.defaultTextEdit.setMaximumHeight(50)
		self.defaultTextEdit.focusOutEvent = lambda s: self.changeText("default")
		
		# Default text without use text
		self.defaultTextLabel2 = QtGui.QLabel("Oletusteksti puuttuville teksteille:")
		self.defaultTextEdit2 = QtGui.QTextEdit()
		self.defaultTextEdit2.setMaximumHeight(50)
		self.defaultTextEdit2.focusOutEvent = lambda s: self.changeText("default")
		
		# Separator
		self.separator = QtGui.QLabel("")
		self.separator.setFrameStyle(QtGui.QFrame.HLine | QtGui.QFrame.Raised)
		
		# Interaction texts
		self.interactionTextGroupBox = QtGui.QGroupBox("Tekstit esinettä käytettäessä muihin esineisiin")
		self.interactionTextLayout = QtGui.QVBoxLayout()
		self.text_scene = QtGui.QTableWidget(self)
		self.interactionTextGroupBox.setLayout(self.interactionTextLayout)
		self.text_scene.cellChanged.connect(self.changeInteractionText)
		
		# Display options for interaction texts
		self.displayOptionGroupBox = QtGui.QGroupBox("Näytä")
		self.displayOptionLayout = QtGui.QHBoxLayout()
		self.displayOptionGroupBox.setLayout(self.displayOptionLayout)
		self.displayAllButton = QtGui.QRadioButton("Kaikki")
		self.displayAllButton.clicked.connect(lambda: self.displayAllInteractions("all"))
		self.displayMissingButton = QtGui.QRadioButton("Puuttuvat")
		self.displayMissingButton.clicked.connect(lambda: self.displayAllInteractions("missing"))
		self.displayDoneButton = QtGui.QRadioButton("Tehdyt")
		self.displayDoneButton.clicked.connect(lambda: self.displayAllInteractions("done"))

	def displayTexts(self, item):
		self.currentItem = item
		self.layout.addWidget(self.clickTextLabel, 0, 0)
		self.layout.addWidget(self.clickTextEdit, 1, 0)
		self.layout.addWidget(self.pickupTextLabel, 0, 1)
		self.layout.addWidget(self.pickupTextEdit, 1, 1)
		self.layout.addWidget(self.useTextLabel, 2, 0)
		self.layout.addWidget(self.useTextEdit, 3, 0)
		self.layout.addWidget(self.defaultTextLabel2, 2, 0)
		self.layout.addWidget(self.defaultTextEdit2, 3, 0)
		self.layout.addWidget(self.defaultTextLabel, 2, 1)
		self.layout.addWidget(self.defaultTextEdit, 3, 1)
		self.layout.addWidget(self.separator, 4, 0, 1, 4)
		self.layout.addWidget(self.interactionTextGroupBox, 5, 0, 3, 3)
		self.layout.addWidget(self.displayOptionGroupBox, 8, 0)
		
		# Display option buttons
		self.displayAllButton.setChecked(True)
		self.displayOptionLayout.addWidget(self.displayAllButton)
		self.displayOptionLayout.addWidget(self.displayMissingButton)
		self.displayOptionLayout.addWidget(self.displayDoneButton)
		
		# Interaction texts
		# TODO: This text_scene should always stretch more than the other widgets
		self.interactionTextLayout.addWidget(self.text_scene)
		self.text_scene.setRowCount(0)
		self.text_scene.setColumnCount(2)
		self.text_scene.setColumnWidth(0, 250)
		self.text_scene.setColumnWidth(1, 250)
		
		# TODO: Texts for open, closed, empty, full, etc.
		self.itemSettings = [
			self.pickupTextLabel,
			self.pickupTextEdit,
			self.useTextLabel,
			self.useTextEdit,
			self.defaultTextLabel,
			self.defaultTextEdit,
			self.defaultTextLabel2,
			self.defaultTextEdit2,
			self.displayOptionGroupBox,
			self.displayAllButton,
			self.displayMissingButton,
			self.displayDoneButton,
			self.interactionTextGroupBox,
		]
		
		# TODO: Secrets are not working right when removing their text
		if (self.currentItem.textItem.imageAttributes["category"] == "secret" or "src2" in self.currentItem.textItem.imageAttributes):
			self.clickTextEdit.setText(self.currentItem.texts["pickup"])
		else:
			if not ("examine" in self.currentItem.texts):
				self.currentItem.texts["examine"] = ""
			else:
				self.clickTextEdit.setText(self.currentItem.texts["examine"])
		
		# Item
		if (self.currentItem.objectType == "Item" and "src2" not in self.currentItem.textItem.imageAttributes):
			for setting in self.itemSettings:
				setting.show()
			
			try:
				self.pickupTextEdit.setText(self.currentItem.texts["pickup"])
			except:
				pass
				
			# Display interactions
			self.displayAllInteractions("all")
				
			try:
				if (self.currentItem.target):
					# TODO: Better text for label?
					self.useTextLabel.setText("Teksti käyttökohteelle ”%s”:" %(self.currentItem.target))
					self.useTextEdit.setText(self.currentItem.useText)
					self.defaultTextLabel2.hide()
					self.defaultTextEdit2.hide()
				else:
					self.useTextLabel.hide()
					self.useTextEdit.hide()
					self.defaultTextLabel.hide()
					self.defaultTextEdit.hide()
			except:
				self.useTextLabel.hide()
				self.useTextEdit.hide()
				
			try:
				self.defaultTextEdit.setText(self.currentItem.texts["default"])
				self.defaultTextEdit2.setText(self.currentItem.texts["default"])
			except:
				pass
		
		# Everyone else
		else:
			for setting in self.itemSettings:
				setting.hide()
	
	def changeText(self, textType, gameObject=None, textEdit=None):
		if not (gameObject):
			gameObject = self.currentItem
			
		if (textType == "click"):
			if not (textEdit):
				textEdit = self.clickTextEdit
			gameObject.textItem.setExamineText(textEdit.toPlainText())
		elif (textType == "pickup"):
			if not (textEdit):
				textEdit = self.pickupTextEdit
			gameObject.parentItem.setPickupText(textEdit.toPlainText())
		elif (textType == "use"):
			if not (textEdit):
				textEdit = self.useTextEdit
			gameObject.parentItem.setUseText(textEdit.toPlainText())
			gameObject.useText = textEdit.toPlainText()
		elif (textType == "default"):
			if not (textEdit):
				textEdit = self.defaultTextEdit
			gameObject.parentItem.setDefaultText(textEdit.toPlainText())
		
		self.parent.drawTextItems()

	def changeInteractionText(self, row, column):
		# TODO: Disable editing on first column
		if not (column == 0):
			targetObject = self.text_scene.item(row, 0)
			try:
				interactionText = self.text_scene.selectedItems()[0].text()
				self.currentItem.parentItem.setInteractionText(targetObject.id, interactionText)
				self.parent.drawTextItems()
			except:
				pass

	def displayAllInteractions(self, displayOption):
		self.text_scene.clear()
		targets = self.scenarioData.getAllObjects()[0]
		self.text_scene.setSortingEnabled(False)
		row = 0
		self.text_scene.setRowCount(0)
		for target in targets:
			for targetImage in target.getImages():
				# Interaction text with the target
				try:
					interactionText = self.currentItem.texts[targetImage.id]
				except:
					interactionText = ""
				
				if (targetImage.id == self.currentItem.id or
					targetImage.imageAttributes["category"] == "secret" or
					(displayOption == "missing" and interactionText != "") or
					(displayOption == "done" and interactionText == "")):
					continue
					
				self.text_scene.insertRow(self.text_scene.rowCount())
				imageObject = self.scenarioData.getJSONObject(targetImage.id)
				# TODO: cell size doesn't work!
				targetItem = TextItemWidget(imageObject, self.scenarioData.getObject(target.id), self.scenarioData.dataDir, 100)
				self.text_scene.setItem(row, 0, targetItem)
				
				interactionTextItem = QtGui.QTableWidgetItem()
				interactionTextItem.setText(interactionText)
				self.text_scene.setItem(row, 1, interactionTextItem)
				
				row += 1
		#self.text_scene.resizeRowsToContents()
		self.text_scene.setSortingEnabled(True)
		
class SpaceViewItem(QtGui.QGraphicsPixmapItem):
	def __init__(self, pixmap, name, parent=None):
		super(SpaceViewItem, self).__init__(pixmap)
		self.name = name
		self.parent = parent

	def mousePressEvent(self, event):
		try:
			roomItems = self.parent.left_scene.currentItem().room.getItems()
		except IndexError:
			return
			
		for item in roomItems:
			if (item.id == self.name):
				selectedItem = item
			else:
				print("Error: item.id not found in roomItems!")
		
		self.parent.settingsWidget.displayOptions(selectedItem)
		self.parent.setRemoveObjectsButtonDisabled()
		self.parent.setRemoveViewsButtonDisabled()
		QtGui.QGraphicsItem.mousePressEvent(self, event)

	def dragMoveEvent(self, event):
		print("dropp")
		QtGui.QGraphicsItem.dragMoveEvent(self, event)

	def mouseReleaseEvent(self, event):
		#itemList = self.parent.spaceScene.collidingItems(self)
		#for item in itemList:
		#	print ("ITEMIIT", item.widget())
		self.parent.settingsWidget.currentObject.setPosition(self.pos())
		print(self.pos())
		QtGui.QGraphicsItem.mouseReleaseEvent(self, event)

	def dropEvent(self, event):
		print("DROOOOP")
		QtGui.QGraphicsItem.dropEvent(self, event)

if __name__ == '__main__':
	from sys import argv, exit

	app = QtGui.QApplication(argv)

	editor = Editor()
	editor.show()
	exit(app.exec_())
