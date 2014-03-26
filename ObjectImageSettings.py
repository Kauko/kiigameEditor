from PySide import QtGui, QtCore

# A widget that may have an object's closed, locked and open state settings
class ObjectImageSettings(QtGui.QWidget):
	def __init__(self, titleLabelText, nameLabelText, canBeLocked=False, lockedText=None, parent=None):
		super(ObjectImageSettings, self).__init__(parent)
		
		self.layout = QtGui.QVBoxLayout()
		self.setLayout(self.layout)
		
		self.parent = parent
		
		self.labelLine = self.parent.createSeparator()
		self.titleLabel = QtGui.QLabel(titleLabelText)
		self.nameLabel = QtGui.QLabel(nameLabelText)
		self.nameEdit = QtGui.QLineEdit()
		
		self.image = QtGui.QLabel(self)
		self.image.mousePressEvent = lambda s: self.parent.showImageDialog(lambda imagePath: self.changeImage(imagePath))
		
		self.clickLabel = QtGui.QLabel("Teksti klikatessa")
		self.clickEdit = QtGui.QTextEdit()
		self.clickEdit.setMaximumHeight(50)
		
		self.layout.addWidget(self.labelLine)
		self.layout.addWidget(self.titleLabel)
		
		self.canBeLocked = canBeLocked
		if (self.canBeLocked):
			# TODO: Texts need to be set from outside
			self.lockedCheckbox = QtGui.QCheckBox(lockedText)
			self.lockedCheckbox.stateChanged.connect(self.changeLocked)
			self.keyLabel = QtGui.QLabel("Mikä avaa?")
			self.keyCombo = self.parent.createItemCombobox("Avainta ei valittu!", ("item",), ("item",), self.clearKey, self.changeKey)
			
			self.layout.addWidget(self.lockedCheckbox)
			self.layout.addWidget(self.keyLabel)
			self.layout.addWidget(self.keyCombo)
			
		self.layout.addWidget(self.nameLabel)
		self.layout.addWidget(self.nameEdit)
		self.layout.addWidget(self.image)
		self.layout.addWidget(self.clickLabel)
		self.layout.addWidget(self.clickEdit)
		
	def clearKey(self):
		print("Clearing key!")
		
	def changeKey(self):
		print("Changing key!")
		
	def changeLocked(self):
		if (self.lockedCheckbox.isChecked()):
			isDisabled = False
		else:
			isDisabled = True
		self.nameLabel.setDisabled(isDisabled)
		self.nameEdit.setDisabled(isDisabled)
		self.keyLabel.setDisabled(isDisabled)
		self.keyCombo.setDisabled(isDisabled)
		self.image.setDisabled(isDisabled)
		self.clickLabel.setDisabled(isDisabled)
		self.clickEdit.setDisabled(isDisabled)
		
		# TODO: Erase locked image, name etc. when unchecked
		
	def changeImage(self, imagePath):
		self.parent.setobjectImage(imagePath, self.image)
		self.gameImageObject.setSource(imagePath)
		
	def setSettings(self, gameObject, gameImageObject):
		self.gameObject = gameObject
		self.gameImageObject = gameImageObject
		self.objectType = self.gameObject.__class__.__name__
		
		# Set image
		if (self.gameImageObject):
			imagePath = self.parent.parent.getImageDir()+"/"+self.gameImageObject.getSource()
		elif self.objectType == "Door":
			imagePath = "images/door_placeholder.png"
		elif self.objectType == "Container":
			imagePath = "images/container_placeholder.png"
		self.parent.setobjectImage(imagePath, self.image)
		
		# Change locked state
		if (self.canBeLocked):
			if (self.objectType == "Obstacle" or gameObject.isLocked()):
				self.lockedCheckbox.setCheckState(QtCore.Qt.CheckState.Checked)
			else:
				self.lockedCheckbox.setCheckState(QtCore.Qt.CheckState.Unchecked)
			self.changeLocked()
			self.setKey()
			
		# Delete checkbox if obstacle
		if (self.objectType == "Obstacle"):
			# Error about having already deleted may appear
			try:
				self.lockedCheckbox.deleteLater()
			except:
				pass
						
		self.parent.setObjectName(self.gameImageObject, "Kulkureitillä", self.nameEdit)
		self.parent.setExamineText(self.gameImageObject, self.clickEdit)
		
	# Set the correct key item in keyCombo
	def setKey(self):
		self.parent.setComboboxIndex(self.gameObject.getKey(), self.keyCombo)
