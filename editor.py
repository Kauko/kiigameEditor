# -*- coding: UTF-8 -*-

# TODO: Pre-cache rooms, images, texts etc. ?

from PySide import QtGui, QtCore
import SettingsWidget, ScenarioData
from ImageCache import ImageCache

class Editor(QtGui.QMainWindow):
	def __init__(self, parent=None):
		super(Editor, self).__init__(parent)
		
		self.scenarioData = ScenarioData.ScenarioData()
		self.scenarioData.loadScenario()
		
		self.imageCache = ImageCache()
		
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
		
		layout = QtGui.QGridLayout()
		self.mainTab.setLayout(layout)
		
		# Room preview
		left_frame = QtGui.QGroupBox("Tilat")
		left_frame_layout = QtGui.QGridLayout()
		left_frame.setLayout(left_frame_layout)
		layout.addWidget(left_frame, 1, 0, 1, 2)
		
		# Set-up widget for showing rooms
		self.left_scene = QtGui.QListWidget(self)
		self.left_scene.setIconSize(QtCore.QSize(200, 200))
		self.left_scene.setViewMode(QtGui.QListView.IconMode)
		self.left_scene.setFlow(QtGui.QListView.LeftToRight)
		self.left_scene.setMovement(QtGui.QListView.Static)
		self.left_scene.itemClicked.connect(self.roomClicked)
		# TODO: Double click room, display the room view
		left_frame_layout.addWidget(self.left_scene)
		
		self.addViewsCombo = QtGui.QComboBox(self)
		self.addViewsCombo.addItem("Lisää tila")
		self.addViewsCombo.addItem("Huone", userData="room")
		self.addViewsCombo.addItem("Välianimaatio", userData="sequence")
		self.addViewsCombo.currentIndexChanged.connect(self.addViewsComboChanged)
		layout.addWidget(self.addViewsCombo, 0, 0)
		
		self.removeViewsButton = QtGui.QPushButton("Poista valittu tila")
		self.setRemoveViewsButtonDisabled()
		self.removeViewsButton.clicked.connect(self.removeViewsButtonClicked)
		layout.addWidget(self.removeViewsButton, 0, 1)
		
		# Draw rooms and select the first one
		self.drawRooms()
		selectedRoom = self.left_scene.itemAt(0, 0)
		self.left_scene.setCurrentItem(selectedRoom)
		
		# Room items
		middle_frame = QtGui.QGroupBox("Huoneen esineet")
		middle_frame_layout = QtGui.QVBoxLayout()
		middle_frame.setLayout(middle_frame_layout)
		layout.addWidget(middle_frame, 1, 2, 1, 2)
		
		# Set-up widget for showing room items
		self.middle_scene = QtGui.QListWidget(self)
		self.middle_scene.setIconSize(QtCore.QSize(100, 100))
		self.middle_scene.setMovement(QtGui.QListView.Static)
		self.middle_scene.itemSelectionChanged.connect(self.roomItemClicked)
		middle_frame_layout.addWidget(self.middle_scene)
		
		self.addObjectsCombo = QtGui.QComboBox(self)
		self.addObjectsCombo.addItem("Lisää esine valittuun huoneeseen")
		self.addObjectsCombo.addItem("Kiinteä esine", userData="object")
		self.addObjectsCombo.addItem("Käyttöesine", userData="item")
		self.addObjectsCombo.addItem("Ovi", userData="door")
		self.addObjectsCombo.addItem("Säiliö", userData="container")
		self.addObjectsCombo.addItem("Este", userData="obstacle")
		self.addObjectsCombo.currentIndexChanged.connect(self.addObjectsComboChanged)
		layout.addWidget(self.addObjectsCombo, 0, 2)
		
		self.removeObjectsButton = QtGui.QPushButton("Poista valittu esine")
		self.setRemoveObjectsButtonDisabled()
		self.removeObjectsButton.clicked.connect(self.removeObjectsButtonClicked)
		layout.addWidget(self.removeObjectsButton, 0, 3)
		
		self.drawRoomItems()
		
		# Settings for items and rooms
		right_frame = QtGui.QGroupBox("Asetukset")
		right_frame_layout = QtGui.QVBoxLayout()
		right_frame.setLayout(right_frame_layout)
		layout.addWidget(right_frame, 1, 4)
		
		self.settingsWidget = SettingsWidget.SettingsWidget(self)
		self.settingsWidget.displayOptions(selectedRoom.room)
		
		# Set settings widget scrollable instead resizing main window
		scrollArea = QtGui.QScrollArea()
		scrollArea.setWidgetResizable(True)
		scrollArea.setWidget(self.settingsWidget)
		right_frame_layout.addWidget(scrollArea)
		
	def addViewsComboChanged(self):
		selected = self.addViewsCombo.itemData(self.addViewsCombo.currentIndex())
		if not (selected in ("room", "sequence")):
			return
		self.createObject(selected)
		
		self.addObjectsCombo.setCurrentIndex(0)
		self.left_scene.setCurrentRow(self.left_scene.count()-1)
		
	def removeViewsButtonClicked(self):
		selected = self.left_scene.currentItem()
		
		row = self.left_scene.currentRow()
		self.left_scene.takeItem(row)
		
		self.drawRoomItems()
		
	def addObjectsComboChanged(self):
		selected = self.addObjectsCombo.itemData(self.addObjectsCombo.currentIndex())
		if not (selected in ("object", "item", "door", "container", "obstacle", )):
			return
		self.createObject(selected)
		
		self.addObjectsCombo.setCurrentIndex(0)
		self.middle_scene.setCurrentRow(self.middle_scene.count()-1)
		
	def removeObjectsButtonClicked(self):
		selected = self.middle_scene.currentItem()
		
		row = self.middle_scene.currentRow()
		self.middle_scene.takeItem(row)
		
	def setRemoveObjectsButtonDisabled(self):
		selected = self.middle_scene.selectedItems()
		if (len(selected) == 0):
			isDisabled = True
		else:
			isDisabled = False
			
		self.removeObjectsButton.setDisabled(isDisabled)
		
	def setRemoveViewsButtonDisabled(self):
		selected = self.left_scene.selectedItems()
		if (len(selected) == 0):
			isDisabled = True
		else:
			isDisabled = False
			
		self.removeViewsButton.setDisabled(isDisabled)
		
	def createSpaceTab(self):
		self.spaceTab = QtGui.QWidget()

		layout = QtGui.QHBoxLayout()
		self.spaceTab.setLayout(layout)
		
		# Another settings widget for room view
		self.spaceSettingsWidget = SettingsWidget.SettingsWidget(self)
		selectedRoom = self.left_scene.selectedItems()[0]
		self.spaceSettingsWidget.displayOptions(selectedRoom.room)

		# Room
		left_frame = QtGui.QGroupBox("Tila")
		left_frame_layout = QtGui.QVBoxLayout()
		left_frame.setLayout(left_frame_layout)
		layout.addWidget(left_frame)

		# Settings
		right_frame = QtGui.QGroupBox("Asetukset")
		right_frame_layout = QtGui.QVBoxLayout()
		right_frame.setLayout(right_frame_layout)
		layout.addWidget(right_frame)
		
		scrollArea = QtGui.QScrollArea()
		scrollArea.setWidgetResizable(True)
		scrollArea.setWidget(self.spaceSettingsWidget)
		
		right_frame_layout.addWidget(scrollArea)
		self.spaceScene = QtGui.QGraphicsScene(self)
		view = QtGui.QGraphicsView(self.spaceScene)
		view.setDragMode(QtGui.QGraphicsView.ScrollHandDrag)
		left_frame_layout.addWidget(view)
		
		self.updateSpaceTab()
	
	def updateSpaceTab(self):
		selectedRoom = self.left_scene.selectedItems()[0]
		self.spaceSettingsWidget.displayOptions(selectedRoom.room)
		
		# Display room image
		pixmap = self.imageCache.createPixmap(self.scenarioData.dataDir + "/" + selectedRoom.room.getRepresentingImage().getSource())
		self.spaceScene.addPixmap(pixmap)
		
		# Display objects
		for item in selectedRoom.room.getItems():
			# TODO: Resolve handling text objects (issue #8)
			if (item.getClassname() == "Text"):
				continue
				
			img = item.getRepresentingImage()
			#print(self.scenarioData.dataDir + "/" + img.getSource())
			pixmap = self.imageCache.createPixmap(self.scenarioData.dataDir + "/" + img.getSource())
			pixItem = QtGui.QGraphicsPixmapItem(pixmap)
			pixItem.setFlag(QtGui.QGraphicsItem.ItemIsMovable)
			
			#TODO: Game crops some amount from the borders, insert that amount into items offset value
			pos = item.getPosition()
			pixItem.setPos(pos[0],pos[1])
			self.spaceScene.addItem(pixItem)
			
	def createObject(self, objectType):
		selectedRoom = self.left_scene.selectedItems()[0]
		if (objectType == "room"):
			newObject = self.scenarioData.addRoom(None, None, None)
			
		elif (objectType == "sequence"):
			print("create sequence")
			
		elif (objectType == "object"):
			newObject = selectedRoom.room.addObject()
		elif (objectType == "item"):
			newObject = selectedRoom.room.addItem()
		elif (objectType == "door"):
			newObject = selectedRoom.room.addDoor()
		elif (objectType == "container"):
			newObject = selectedRoom.room.addContainer()
		elif (objectType == "obstacle"):
			newObject = selectedRoom.room.addObstacle()
		else:
			return
		print("new ovject", newObject, newObject.id)
		
		#widget.setRepresentingImage("airfreshener.png")
		newObject.getRepresentingImage().setSource("airfreshener.png")
		widgetItem = ItemWidget(newObject, self.scenarioData.dataDir)
		self.middle_scene.addItem(widgetItem)
		
	# Click on a room in the main tab
	def roomClicked(self):
		self.drawRoomItems()
		self.settingsWidget.displayOptions(self.left_scene.selectedItems()[0].room)
		self.updateSpaceTab()
		self.setRemoveViewsButtonDisabled()
		
	# Click on an item in the main tab room preview
	def roomItemClicked(self):
		# TODO: Clear when suitable (like when no items in the view)
		selected = self.middle_scene.currentItem()
		if (selected):
			self.settingsWidget.displayOptions(selected.item)
			
		self.setRemoveObjectsButtonDisabled()
		
	# Draw the leftmost frame items
	def drawRooms(self):
		self.left_scene.clear()
		
		# Rooms
		for i in range(len(self.scenarioData.roomList)):
			room = self.scenarioData.roomList[i]
			widgetItem = ViewWidget(room, self.scenarioData.dataDir)
			
			self.left_scene.addItem(widgetItem)
			
		# Sequences
		for i in range(len(self.scenarioData.sequenceList)):
			sequence = self.scenarioData.sequenceList[i]
			widgetItem = ViewWidget(sequence, self.scenarioData.dataDir)
			
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
			# TODO: Resolve handling text objects (issue #8)
			if (item.getClassname() == "Text"):
				continue
				
			widgetItem = ItemWidget(item, self.scenarioData.dataDir)
			
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
		
		roomName = room.getName()
		if not (roomName):
			# TODO: Some common delegate for these namings
			roomName = "Tilalla ei ole nimeä"
		self.setText(roomName)
		
		imagePath = imageDir+"/"+room.getRepresentingImage().getSource()
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
		
		imagePath = imageDir+"/"+imageObject.getSource()
		icon = QtGui.QIcon(imagePath)
		self.setIcon(icon)
							
if __name__ == '__main__':
	from sys import argv, exit

	app = QtGui.QApplication(argv)

	editor = Editor()
	editor.show()
	exit(app.exec_())
