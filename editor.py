# -*- coding: UTF-8 -*-

# TODO: Encoding that works better with Pyside

from PySide import QtGui, QtCore
import ScenarioData

class Editor(QtGui.QMainWindow):
	def __init__(self, parent=None):
		super(Editor, self).__init__(parent)
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
		left_frame_layout = QtGui.QVBoxLayout()
		left_frame.setLayout(left_frame_layout)
		
		left_scene = QtGui.QGraphicsScene(self)
		
		left_view = QtGui.QGraphicsView(left_scene)
		left_frame_layout.addWidget(left_view, 1, 1)
		layout.addWidget(left_frame)
		
		#All the pictures are in the same place
		#TODO: implement QGraphicsGridLayout
		#TODO: Also parser the other attributes and show them (names, etc.)
		for i in range(len(ScenarioData.sc.roomList)):
			pixmap = QtGui.QPixmap(ScenarioData.sc.getRoomBackLoc(i)).scaled(150, 150, QtCore.Qt.KeepAspectRatio)
			pixItem = QtGui.QGraphicsPixmapItem(pixmap)
			left_scene.addItem(pixItem)
			
		# Room items
		#TODO: Same parsering as above
		middle_frame = QtGui.QGroupBox("Huoneen esineet")
		middle_frame_layout = QtGui.QVBoxLayout()
		middle_frame.setLayout(middle_frame_layout)
		layout.addWidget(middle_frame)
		
		# Settings for items and rooms
		right_frame = QtGui.QGroupBox("Asetukset")
		right_frame_layout = QtGui.QVBoxLayout()
		right_frame.setLayout(right_frame_layout)
		layout.addWidget(right_frame)

		middle_frame_layout.addWidget(RoomWidget("Hello world!"))
		middle_frame_layout.addWidget(RoomWidget("Hello world!"))
		middle_frame_layout.addWidget(RoomWidget("Hello world!"))
		middle_frame_layout.addWidget(RoomWidget("Hello world!"))

		right_frame_layout.addWidget(SettingsWidget())

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
		print(ScenarioData.sc.getRoomBackLoc(0))
		print(ScenarioData.sc.getObjectImgLoc(0, 0))
		pixmap = QtGui.QPixmap(ScenarioData.sc.getRoomBackLoc(0)).scaled(790, 534, QtCore.Qt.KeepAspectRatio)
		scene.addPixmap(pixmap)
		
		left_frame_layout.addWidget(view)

		# Settings
		right_frame = QtGui.QGroupBox("Asetukset")
		right_frame_layout = QtGui.QVBoxLayout()
		right_frame.setLayout(right_frame_layout)
		layout.addWidget(right_frame)

		right_frame_layout.addWidget(SettingsWidget(self))

# Room image with caption used in the main view
class RoomWidget(QtGui.QWidget):
	def __init__(self, caption_text, parent=None):
		super(RoomWidget, self).__init__(parent)
		self.setAutoFillBackground(True)
		
		layout = QtGui.QVBoxLayout()
		self.setLayout(layout)

		# Display image
		scene = QtGui.QGraphicsScene(self)
		view = QtGui.QGraphicsView(scene)
		
		pixmap = QtGui.QPixmap("gamedata/latkazombit/images/character_panic.png")
		scene.addPixmap(pixmap)
		
		layout.addWidget(view)
		
		# Image caption text
		caption = QtGui.QLabel(self)
		caption.setText(caption_text)
		
		layout.addWidget(caption)

# Item and room settings widget
class SettingsWidget(QtGui.QWidget):
	def __init__(self, parent=None):
		super(SettingsWidget, self).__init__(parent)

		# For testing the different options:
		self.showObjectOptions()
		#self.showRoomOptions()
		
	#Settings for the object view
	#TODO: Reduce redundancy; similar settings layout, "Name", "Picture" etc., are defined many times
	def showObjectOptions(self):
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
	def showRoomOptions(self):
		# TODO: Align the layout to the top
		layout = QtGui.QGridLayout()
		self.setLayout(layout)
		self.setSizePolicy(QtGui.QSizePolicy(
		QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed))
		
		nameLabel = QtGui.QLabel("Nimi")
		nameEdit = QtGui.QLineEdit("Huone1")
		# Room image
		imgTextLabel = QtGui.QLabel("Kuva")
		imgPixmap = QtGui.QPixmap("gamedata/latkazombit/images/shower_room.png").scaled(200, 200, QtCore.Qt.KeepAspectRatio)
		imgLabel = QtGui.QLabel(self)
		imgLabel.setPixmap(imgPixmap)

		musicLabel = QtGui.QLabel("Musiikki")
		musicTextEdit = QtGui.QLineEdit("Placeholder.mp3")
		musicTextEdit.setReadOnly(True)
		# TODO: QFileDialog to select the music, doesn't work yet
		musicBtn = QtGui.QPushButton('Selaa...', self)
		musicBtn.setToolTip('Valitse musiikkitiedosto')
		musicBtn.resize(musicBtn.sizeHint())
		musicBtn.clicked.connect(self.showDialog)
		
		whereFromLabel = QtGui.QLabel("Mista sinne paasee?")
		whereFromCombo = QtGui.QComboBox(self)
		whereFromCombo.setIconSize(QtCore.QSize(50,50))
		roomIcon = QtGui.QIcon(imgPixmap)
		# Example rooms
		whereFromCombo.addItem(roomIcon, "Huone2")
		whereFromCombo.addItem(roomIcon, "Huone3")
		whereFromCombo.addItem(roomIcon, "Huone4")
		
		layout.addWidget(nameLabel, 0, 0)
		layout.addWidget(nameEdit, 0, 1, 1, 2)
		layout.addWidget(imgTextLabel, 1, 0)
		layout.addWidget(imgLabel, 1, 1, 2, 2)
		layout.addWidget(musicLabel, 4, 0)
		layout.addWidget(musicTextEdit, 4, 1)
		layout.addWidget(musicBtn, 4, 2)
		layout.addWidget(whereFromLabel, 6, 0)
		layout.addWidget(whereFromCombo, 6, 1, 1, 2)
	
	def showDialog(self):
		fname, _ = QtGui.QFileDialog.getOpenFileName(self,
		'Valitse musiikkitiedosto','/home/', "Musiikkitiedostot (*.mp3 *.ogg)")
		
		#f = open(fname, 'r')
		#with f:
		#	data = f.read()
		#	self.musicTextEdit.setText(fname.selectedFiles)

class DropDownWidget(QtGui.QWidget):
	def __init__(self, parent=None):
		super(SettingsWidget, self).__init__(parent)
		print("Dropdown widget!")

if __name__ == '__main__':
	from sys import argv, exit

	app = QtGui.QApplication(argv)

	editor = Editor()
	editor.show()
	exit(app.exec_())
