# -*- coding: UTF-8 -*-

# TODO: Encoding that works better with Pyside

from PySide import QtGui
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
		left_frame_layout = QtGui.QGridLayout()
		left_frame.setLayout(left_frame_layout)
		layout.addWidget(left_frame)
		
		# Room items
		middle_frame = QtGui.QGroupBox("Huoneen esineet")
		middle_frame_layout = QtGui.QVBoxLayout()
		middle_frame.setLayout(middle_frame_layout)
		layout.addWidget(middle_frame)
		
		# Settings for items and rooms
		right_frame = QtGui.QGroupBox("Asetukset")
		right_frame_layout = QtGui.QVBoxLayout()
		right_frame.setLayout(right_frame_layout)
		layout.addWidget(right_frame)
		
		left_frame_layout.addWidget(RoomWidget("Hello world!"), 0, 0)
		left_frame_layout.addWidget(RoomWidget("Hello world!"), 1, 0)
		left_frame_layout.addWidget(RoomWidget("Hello world!"), 0, 1)
		left_frame_layout.addWidget(RoomWidget("Hello world!"), 1, 1)

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
		left_frame = QtGui.QWidget(self)
		left_frame_layout = QtGui.QVBoxLayout()
		left_frame.setLayout(left_frame_layout)
		layout.addWidget(left_frame)

		# Display room image
		scene = QtGui.QGraphicsScene(self)
		view = QtGui.QGraphicsView(scene)
		
		pixmap = QtGui.QPixmap("graphics/intro_5.png")
		scene.addPixmap(pixmap)
		
		left_frame_layout.addWidget(view)

		# Settings
		right_frame = QtGui.QWidget(self)
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
		
		pixmap = QtGui.QPixmap("graphics/character_panic.png")
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
		
		# TODO: Stop the vertical stretching/padding
		layout = QtGui.QGridLayout()
		self.setLayout(layout)
		self.setSizePolicy(QtGui.QSizePolicy(
		QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Fixed))
		
		# TODO: Function to change the layout according to what is chosen
		# These are for the room settings
		nameLabel = QtGui.QLabel("Nimi")
		nameEdit = QtGui.QLineEdit("Huone1")
		# Room image
		roomImgScene = QtGui.QGraphicsScene(self)
		roomImgView = QtGui.QGraphicsView(roomImgScene)
		imgLabel = QtGui.QLabel("Kuva")
		imgPixmap = QtGui.QPixmap("graphics/shower_room.png").scaledToHeight(150)
		roomImgScene.addPixmap(imgPixmap)
		musicLabel = QtGui.QLabel("Musiikki")
		musicTextEdit = QtGui.QLineEdit("Placeholder.mp3")
		musicTextEdit.setReadOnly(True)
		# TODO: QFileDialog to select the music, doesn't work yet
		musicBtn = QtGui.QPushButton('Selaa...', self)
		musicBtn.setToolTip('Valitse musiikkitiedosto')
		musicBtn.resize(musicBtn.sizeHint())
		musicBtn.clicked.connect(self.showDialog)
		
		whereFromLabel = QtGui.QLabel("Mista sinne paasee?")
		
		layout.addWidget(nameLabel, 0, 0)
		layout.addWidget(nameEdit, 0, 1, 1, 2)
		layout.addWidget(imgLabel, 1, 0)
		layout.addWidget(roomImgView, 1, 1, 2, 2)
		layout.addWidget(musicLabel, 4, 0)
		layout.addWidget(musicTextEdit, 4, 1)
		layout.addWidget(musicBtn, 4, 2)
		layout.addWidget(whereFromLabel, 6, 0)
		#layout.setRowStretch(6, 100)
	
	def showDialog(self):
		fname, _ = QtGui.QFileDialog.getOpenFileName(self,
		'Valitse musiikkitiedosto','/home/', "Musiikkitiedostot (*.mp3 *.ogg)")
		
		f = open(fname, 'r')
		with f:
			data = f.read()
			self.musicTextEdit.setText(data)

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
