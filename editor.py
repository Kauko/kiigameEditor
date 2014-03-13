# -*- coding: UTF-8 -*-

# TODO: Encoding that works better with Pyside

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
		
		self.settingsWidget.showRoomOptions(selectedRoom.room)
		
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

		right_frame_layout.addWidget(SettingsWidget(self))
		
	# Click on a room in the main tab
	def roomClicked(self, widgetItem):
		roomItems = widgetItem.room.getItems()
		self.drawRoomItems(roomItems)
		
	# Clicm on an item in thre main tab room preview
	def roomItemClicked(self, widgetItem):
		print("Room item clicked", widgetItem)
	
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
		
	def getRoomObjects(self):
		return self.scenarioData.getRooms()
		
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
		self.parent = parent
		
		self.musicTextEdit = QtGui.QLineEdit()
		self.musicTextEdit.setReadOnly(True)
		
		self.imgLabel = QtGui.QLabel(self)
		self.imgLabel.mousePressEvent = lambda s: self.showImageDialog()
		# For testing the different options:
		#self.showObjectOptions()
		#self.showRoomOptions()
		
	#Settings for the object view
	#TODO: Reduce redundancy; similar settings layout, "Name", "Picture" etc., are defined many times
	def showObjectOptions(self, gameObject):
		layout = QtGui.QGridLayout()
		self.setLayout(layout)
		self.setSizePolicy(QtGui.QSizePolicy(
		QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed))
		
		nameLabel = QtGui.QLabel("Nimi")
		nameEdit = QtGui.QLineEdit("Nalle1")
		# Object image
		imgTextLabel = QtGui.QLabel("Kuva")
		imgPixmap = QtGui.QPixmap("gamedata/latkazombit/images/teddybear.png").scaled(200, 200, QtCore.Qt.KeepAspectRatio)
		imgLabel = QtGui.QLabel(self)
		imgLabel.setPixmap(imgPixmap)

		clickTextLabel = QtGui.QLabel("Teksti klikatessa:")
		clickTextEdit = QtGui.QTextEdit("Sopo nalle etc.")
		clickTextEdit.setMaximumHeight(50)
		
		pickupLabel = QtGui.QLabel("Poiminta")
		pickupLabelLine = QtGui.QLabel("")
		pickupLabelLine.setFrameStyle(QtGui.QFrame.HLine | QtGui.QFrame.Raised)
		
		pickupTextLabel = QtGui.QLabel("Teksti poimittaessa:")
		pickupTextEdit = QtGui.QTextEdit("Mitahan tama taalla tekee?")
		pickupTextEdit.setMaximumHeight(50)
		
		pickupBlockLabel = QtGui.QLabel("Estaako jokin poiminnan?")
		pickupBlockCombo = QtGui.QComboBox(self)
		pickupBlockCombo.setIconSize(QtCore.QSize(50,50))
		obstacleIcon = QtGui.QIcon(imgPixmap)
		# Example obstacles
		pickupBlockCombo.addItem(obstacleIcon, "Morko1")
		pickupBlockCombo.addItem(obstacleIcon, "Morko2")
		pickupBlockCombo.addItem(obstacleIcon, "Morko3")
		
		useLabel = QtGui.QLabel("Kaytto")
		useLabelLine = QtGui.QLabel("")
		useLabelLine.setFrameStyle(QtGui.QFrame.HLine | QtGui.QFrame.Raised)
		useTypeCombo = QtGui.QComboBox(self)
		#TODO: Change according to what is chosen here
		useTypeCombo.addItem("Ei kayttoa")
		useTypeCombo.addItem("Kayta toiseen esineeseen")
		useTypeCombo.addItem("Avaa jotakin")
		useTypeCombo.addItem("Laita johonkin")
		useTargetCombo = QtGui.QComboBox(self)
		useTargetCombo.setIconSize(QtCore.QSize(50,50))
		targetIcon = QtGui.QIcon(imgPixmap)
		useTargetCombo.addItem(targetIcon, "Kohde1")
		useTargetCombo.addItem(targetIcon, "Kohde2")
		useTargetCombo.addItem(targetIcon, "Kohde3")
		useTextLabel = QtGui.QLabel("Teksti kaytettaessa:")
		useTextEdit = QtGui.QTextEdit("Kaappihan aukesi!")
		useTextEdit.setMaximumHeight(50)
		
		allTextsButton = QtGui.QPushButton("Nama ja muut tekstit")
		
		layout.addWidget(nameLabel, 0, 0)
		layout.addWidget(nameEdit, 0, 1, 1, 2)
		layout.addWidget(imgTextLabel, 1, 0)
		layout.addWidget(imgLabel, 1, 1, 2, 2)
		layout.addWidget(clickTextLabel, 4, 0)
		layout.addWidget(clickTextEdit, 4, 1)
		layout.addWidget(pickupLabelLine, 5, 0, 1, 2)
		layout.addWidget(pickupLabel, 6, 0)
		layout.addWidget(pickupTextLabel, 7, 0)
		layout.addWidget(pickupTextEdit, 7, 1)
		layout.addWidget(pickupBlockLabel, 8, 0)
		layout.addWidget(pickupBlockCombo, 8, 1)
		layout.addWidget(useLabelLine, 9, 0, 1, 2)
		layout.addWidget(useLabel, 10, 0)
		layout.addWidget(useTypeCombo, 11, 1)
		layout.addWidget(useTargetCombo, 12, 1)
		layout.addWidget(useTextLabel, 13, 0)
		layout.addWidget(useTextEdit, 13, 1)
		layout.addWidget(allTextsButton, 14, 1)
		
	
	#Settings for the room view
	def showRoomOptions(self, gameRoom):
		#TODO: Change room attributes in real time or after closing the dialog?
		
		# TODO: Align the layout to the top
		layout = QtGui.QGridLayout()
		self.setLayout(layout)
		self.setSizePolicy(QtGui.QSizePolicy(
		QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed))
		
		nameLabel = QtGui.QLabel("Nimi")
		roomName = gameRoom.getName()
		if not (roomName):
			roomName = "Huoneella ei ole nimeä"
		nameEdit = QtGui.QLineEdit(roomName)
		
		# Room image
		imgTextLabel = QtGui.QLabel("Kuva")
		self.setRoomBackground(self.parent.getImageDir()+"/"+gameRoom.getBackground().getLocation())
		
		musicLabel = QtGui.QLabel("Musiikki")
		# TODO: Splitting requires detecting OS file slash direction?
		# Get the plain filename for the music
		try:
			roomMusic = gameRoom.getMusic().split("/")[-1]
		except AttributeError:
			# May return None which doesn't have split
			roomMusic = ""
		self.musicTextEdit.setText(roomMusic)
		# TODO: How to clear music?
		
		musicBtn = QtGui.QPushButton('Selaa...', self)
		musicBtn.setToolTip('Valitse musiikkitiedosto')
		musicBtn.resize(musicBtn.sizeHint())
		musicBtn.clicked.connect(self.showMusicDialog)
		
		whereFromLabel = QtGui.QLabel("Mistä sinne pääsee?")
		whereFromCombo = QtGui.QComboBox(self)
		whereFromCombo.setIconSize(QtCore.QSize(50,50))
		
		self.createRoomComboBox(whereFromCombo)
		#roomIcon = QtGui.QIcon(imgPixmap)
		# Example rooms
		#whereFromCombo.addItem(roomIcon, "Huone2")
		#whereFromCombo.addItem(roomIcon, "Huone3")
		#whereFromCombo.addItem(roomIcon, "Huone4")
		
		layout.addWidget(nameLabel, 0, 0)
		layout.addWidget(nameEdit, 0, 1, 1, 2)
		layout.addWidget(imgTextLabel, 1, 0)
		layout.addWidget(self.imgLabel, 1, 1, 2, 2)
		layout.addWidget(musicLabel, 4, 0)
		layout.addWidget(self.musicTextEdit, 4, 1)
		layout.addWidget(musicBtn, 4, 2)
		layout.addWidget(whereFromLabel, 6, 0)
		layout.addWidget(whereFromCombo, 6, 1, 1, 2)
		
	def showMusicDialog(self):
		# TODO: How to remember last folder? (Did adding ~ do this suddenly?)
		# TODO: OS file slash detection here too
		fname, _ = QtGui.QFileDialog.getOpenFileName(self,
		'Valitse musiikkitiedosto','~', "Musiikkitiedostot (*.mp3 *.ogg)")
		# TODO: Modified object requires filename in format "audio/filename.xxx"
		self.musicTextEdit.setText(fname.split("/")[-1])
		
	def showImageDialog(self):
		# TODO: How to remember last folder? (Did adding ~ do this suddenly?)
		# TODO: OS file slash detection here too
		fname, _ = QtGui.QFileDialog.getOpenFileName(self,
		'Valitse taustakuva','~', "Taustakuvat (*.png)")
		# TODO: Modified object requires filename in format "images/filename.png"
		self.setRoomBackground(fname)
		
	def setRoomBackground(self, imagePath):
		imgPixmap = QtGui.QPixmap(imagePath).scaled(200, 200, QtCore.Qt.KeepAspectRatio)
		self.imgLabel.setPixmap(imgPixmap)
		
	def createRoomComboBox(self, combobox):
		for room in self.parent.getRoomObjects():
			# TODO: Some model to eliminate redundancy of this kind of getName/filename patterns
			roomName = room.getName()
			if not (roomName):
				roomName = "Huoneella ei ole nimeä"
			imgPixmap = QtGui.QPixmap(self.parent.getImageDir()+"/"+room.getBackground().getLocation())
			
			roomIcon = QtGui.QIcon(imgPixmap)
			combobox.addItem(roomIcon, roomName)
		#whereFromCombo.addItem(roomIcon, "Huone2")
		
if __name__ == '__main__':
	from sys import argv, exit

	app = QtGui.QApplication(argv)

	editor = Editor()
	editor.show()
	exit(app.exec_())
