# -*- coding: UTF-8 -*-

# TODO: Coding that works better with Pyside

from PySide import QtCore, QtGui

class MainWindow(QtGui.QMainWindow):
    def __init__(self, parent=None):
		super(MainWindow, self).__init__(parent)
		self.setWindowTitle("Kiigame - Pelieditori")
				
		tabWidget = QtGui.QTabWidget()
		self.setCentralWidget(tabWidget)
		
		tabWidget.addTab(GeneralTab(), "Päänäkymä")
		tabWidget.addTab(RoomTab(), "Tila")

class GeneralTab(QtGui.QWidget):
    def __init__(self, parent=None):
		super(GeneralTab, self).__init__(parent)
		
		layout = QtGui.QHBoxLayout()
		self.setLayout(layout)
		
		# Room preview
		left_frame = QtGui.QWidget(self)
		left_frame.setMaximumWidth(500)
		left_frame_layout = QtGui.QGridLayout()
		left_frame.setLayout(left_frame_layout)
		layout.addWidget(left_frame)
		
		# Room items
		middle_frame = QtGui.QWidget(self)
		middle_frame.setMaximumWidth(500)
		middle_frame_layout = QtGui.QVBoxLayout()
		middle_frame.setLayout(middle_frame_layout)
		layout.addWidget(middle_frame)
		
		# Settings for items and rooms
		right_frame = QtGui.QWidget(self)
		right_frame.setMaximumWidth(500)
		right_frame_layout = QtGui.QVBoxLayout()
		right_frame.setLayout(right_frame_layout)
		layout.addWidget(right_frame)
		
		left_frame_layout.addWidget(RoomWidget("Hello world!"), 1, 0)
		left_frame_layout.addWidget(RoomWidget("Hello world!"), 1, 1)
		left_frame_layout.addWidget(RoomWidget("Hello world!"), 2, 0)
		left_frame_layout.addWidget(RoomWidget("Hello world!"), 2, 1)

		middle_frame_layout.addWidget(RoomWidget("Hello world!"))
		middle_frame_layout.addWidget(RoomWidget("Hello world!"))
		middle_frame_layout.addWidget(RoomWidget("Hello world!"))
		middle_frame_layout.addWidget(RoomWidget("Hello world!"))

		right_frame_layout.addWidget(RoomWidget("Hello world!"))

# TODO: Different for sequences?
class RoomTab(QtGui.QWidget):
    def __init__(self, parent=None):
		super(RoomTab, self).__init__(parent)

		layout = QtGui.QHBoxLayout()
		self.setLayout(layout)

		# Room
		left_frame = QtGui.QWidget(self)
		left_frame_layout = QtGui.QVBoxLayout()
		left_frame.setLayout(left_frame_layout)
		layout.addWidget(left_frame)

		# Display room image
		scene = QtGui.QGraphicsScene(self)
		view = QtGui.QGraphicsView(scene)
		
		pixmap = QtGui.QPixmap("intro_5.png")
		scene.addPixmap(pixmap)
		
		left_frame_layout.addWidget(view)

		# Settings
		right_frame = QtGui.QWidget(self)
		right_frame_layout = QtGui.QVBoxLayout()
		right_frame.setLayout(right_frame_layout)
		layout.addWidget(right_frame)

		right_frame_layout.addWidget(SettingsWidget(self))

class SettingsWidget(QtGui.QWidget):
	def __init__(self, parent=None):
		super(SettingsWidget, self).__init__(parent)
		
		layout = QtGui.QVBoxLayout()
		self.setLayout(layout)

		layout.addWidget(QtGui.QLabel("Settings"))

# TODO: No need for this to be a class?
class RoomWidget(QtGui.QWidget):
    def __init__(self, caption_text, parent=None):
		super(RoomWidget, self).__init__(parent)
		self.setAutoFillBackground(True)
		
		layout = QtGui.QVBoxLayout()
		self.setLayout(layout)

		# Display image
		scene = QtGui.QGraphicsScene(self)
		view = QtGui.QGraphicsView(scene)
		
		pixmap = QtGui.QPixmap("character_panic.png")
		scene.addPixmap(pixmap)
		
		layout.addWidget(view)
		
		# Image caption text
		caption = QtGui.QLabel(self)
		caption.setText(caption_text)
		
		layout.addWidget(caption)

if __name__ == '__main__':
	from sys import argv, exit

	app = QtGui.QApplication(argv)
	mainWindow = MainWindow()
	mainWindow.show()
	exit(app.exec_())
