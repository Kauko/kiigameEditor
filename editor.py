# -*- coding: UTF-8 -*-

# TODO: Pre-cache rooms, images, texts etc. ?

from PySide import QtGui, QtCore
import SettingsWidget
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
		self.createTextsTab()
		
		tabWidget.addTab(self.mainTab, "Päänäkymä")
		tabWidget.addTab(self.spaceTab, "Tila")
		tabWidget.addTab(self.textsTab, "Tekstit")
		
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
		
		#right_frame_layout.addWidget(self.settingsWidget)
		
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
		self.text_scene.itemClicked.connect(self.textItemClicked)
		
		left_frame_layout.addWidget(self.text_scene)
		
		# Draw all items and their progress bar
		objects = self.scenarioData.getAllObjects()
		self.drawTextItems(objects)
		
		# Select the first item
		selectedItem = self.text_scene.itemAt(0, 0)
		self.text_scene.setCurrentItem(selectedItem)
		
		# Texts
		right_frame = QtGui.QGroupBox("Tekstit")
		right_frame_layout = QtGui.QVBoxLayout()
		right_frame.setLayout(right_frame_layout)
		layout.addWidget(right_frame)
		
		self.textsWidget = TextsWidget(self)
		self.textsWidget.displayTexts(selectedItem)
		
	# Click on an object in the texts tab object list
	def textItemClicked(self, item):
		self.textsWidget.displayOptions(item)
		
	def drawTextItems(self, textItems):
		row = 0
		imgCount = textItems.pop()
		textItems = textItems.pop()
		
		self.text_scene.setRowCount(0)
		self.text_scene.setColumnCount(2)
		
		#Disable sorting for row count, enable it after adding items
		self.text_scene.setSortingEnabled(False)
		
		for item in textItems:
			# Add a row
			self.text_scene.insertRow(self.text_scene.rowCount())
			
			# Add a text item to the first column
			widgetItem = TextItemWidget(item, self.scenarioData.dataDir)
			self.text_scene.setItem(row, 0, widgetItem)
			
			# Maximum amount of texts for item, 1 for examine
			maxAmount = 1
			#TODO: Rewards are not items? Their maxAmount is just 1

			if (item.__class__.__name__ == "Item"):
				print("Item", item.__class__.__name__)
				maxAmount = imgCount+1
				
				if ("src2" in item.getRepresentingImage().imageAttributes):
					maxAmount = 1
				
			elif not (item.__class__.__name__ == "Object"):
				print("Not Object", item.__class__.__name__)
				maxAmount = len(item.getImages())
				
			# Add a progressbar to the second column
			#progressBarItem = ProgressBarItemWidget(item, maxAmount)
			progressBar = QtGui.QProgressBar()
		
			print ("LOL", item.id, maxAmount, len(item.texts)-1)
			progressBar.setMinimum(0)
			progressBar.setMaximum(maxAmount)
			progressBar.setValue(len(item.texts)-1)
			
			# TODO: Sorting doesn't work, fix possibly by setItem here and setCellWidget inside item
			self.text_scene.setCellWidget(row, 1, progressBar)
			
			row += 1
		self.text_scene.setSortingEnabled(True)
	
	# Click on a room in the main tab
	def roomClicked(self, widgetItem):
		roomItems = widgetItem.room.getItems()
		self.drawRoomItems(roomItems)
		self.settingsWidget.displayOptions(widgetItem.room)
		
	# Click on an item in thre main tab room preview
	def roomItemClicked(self, widgetItem):
		self.settingsWidget.displayOptions(widgetItem.item)
		
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

# Text item widget that represents items in texts tab
class TextItemWidget(QtGui.QTableWidgetItem):
	def __init__(self, textItem, imageDir, parent=None):
		super(TextItemWidget, self).__init__(parent)
		
		# Row size, especially height
		self.setSizeHint(QtCore.QSize(25,25))
		
		self.textItem = textItem
		imageObject = textItem.getRepresentingImage()
		
		textItemName = self.textItem.getName()
		if not (textItemName):
			textItemName = "Esineellä ei ole nimeä"
		self.setText(textItemName)
		
		imagePath = imageDir+"/"+imageObject.getLocation()
		icon = QtGui.QIcon(imagePath)
		self.setIcon(icon)

# ProgressBar item that shows how much item has texts completed
class ProgressBarItemWidget(QtGui.QTableWidgetItem):
	def __init__(self, textItem, maxAmount, parent=None):
		super(ProgressBarItemWidget, self).__init__(parent)
		
		self.progressBar = QtGui.QProgressBar()
		self.textItem = textItem
		self.maxAmount = maxAmount
		
		self.calculateProgress()

	def calculateProgress(self): # If there's many images, .texts doesn't work!
		
		if (self.textItem.__class__.__name__ == "Item"):
			self.maxAmount += 1
		
		print ("LOL", self.textItem.id, self.maxAmount, len(self.textItem.texts)-1)
		self.progressBar.setMinimum(0)
		self.progressBar.setMaximum(self.maxAmount)
		self.progressBar.setValue(len(self.textItem.texts)-1)

# Texts widget that shows texts of specific item in the texts tab
class TextsWidget(QtGui.QWidget):
	def __init__(self, parent=None):
		super(TextsWidget, self).__init__(parent)

	def displayTexts(self, item):
		print("LOOOOO")
							
if __name__ == '__main__':
	from sys import argv, exit

	app = QtGui.QApplication(argv)

	editor = Editor()
	editor.show()
	exit(app.exec_())
