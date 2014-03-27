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
		self.middle_scene.itemSelectionChanged.connect(self.roomItemClicked)
		
		middle_frame_layout.addWidget(self.middle_scene)
		
		self.drawRoomItems()
		#selectedItem = self.middle_scene.itemAt(0, 0)
		#self.middle_scene.setCurrentItem(selectedItem)
		
		# Settings for items and rooms
		right_frame = QtGui.QGroupBox("Asetukset")
		right_frame_layout = QtGui.QVBoxLayout()
		right_frame.setLayout(right_frame_layout)
		layout.addWidget(right_frame)
		
		self.settingsWidget = SettingsWidget.SettingsWidget(self)
		self.settingsWidget.displayOptions(selectedRoom.room)
		
		# Set settings widget scrollable instead resizing main window
		scrollArea = QtGui.QScrollArea()
		scrollArea.setWidgetResizable(True)
		scrollArea.setWidget(self.settingsWidget)
		right_frame_layout.addWidget(scrollArea)
		
	def createSpaceTab(self):
		self.spaceTab = QtGui.QWidget()

		layout = QtGui.QHBoxLayout()
		self.spaceTab.setLayout(layout)
		
		# Another settings widget for room view
		self.spaceSettingsWidget = SettingsWidget.SettingsWidget(self)
		selectedRoom = self.left_scene.selectedItems()[0]
		self.spaceSettingsWidget.displayOptions(selectedRoom.room)

		# Room
		left_frame = QtGui.QGroupBox("Huone")
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
			
			# TODO: Items appear in slightly wrongs places
			# TODO: Combination items like purkkainen nalle showing up?
			# TODO: Some doors are missing
			img = item.getRepresentingImage()
			print(self.scenarioData.dataDir + "/" + img.getSource())
			pixmap = self.imageCache.createPixmap(self.scenarioData.dataDir + "/" + img.getSource())
			pixItem = QtGui.QGraphicsPixmapItem(pixmap)
			
			pos = item.getPosition()
			pixItem.setPos(pos[0],pos[1])
			self.spaceScene.addItem(pixItem)
		
	# Click on a room in the main tab
	def roomClicked(self):
		self.drawRoomItems()
		self.settingsWidget.displayOptions(self.left_scene.selectedItems()[0].room)
		
		self.updateSpaceTab()
		self.settingsWidget.displayOptions(widgetItem.room)
		
	# Click on an item in the main tab room preview
	def roomItemClicked(self):
		selected = self.middle_scene.selectedItems()
		if (len(selected) > 0):
			self.settingsWidget.displayOptions(selected[0].item)
		
	# Draw the leftmost frame rooms
	def drawRooms(self):
		self.left_scene.clear()
		for i in range(len(self.scenarioData.roomList)):
			room = self.scenarioData.roomList[i]
			widgetItem = RoomWidget(room, self.scenarioData.dataDir)
			
			self.left_scene.addItem(widgetItem)
			
	# Draw the middle frame room items
	def drawRoomItems(self):
		self.middle_scene.clear()
		
		roomItems = self.left_scene.selectedItems()[0].room.getItems()
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
		
	# Get the general object name for an object type
	def getGeneralName(self, objectType):
		return self.scenarioData.getGeneralName(objectType)
		
# Room image with caption used in the main view
class RoomWidget(QtGui.QListWidgetItem):
	def __init__(self, room, imageDir, parent=None):
		super(RoomWidget, self).__init__(parent)
		
		self.room = room
		
		roomName = room.getName()
		if not (roomName):
			# TODO: Some common delegate for these namings
			roomName = "Huoneella ei ole nimeä"
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
