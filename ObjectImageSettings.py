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
		self.nameEdit.focusOutEvent = lambda s: self.changeNameEdit()
		
		self.image = QtGui.QLabel(self)
		self.image.mousePressEvent = lambda s: self.parent.showImageDialog(lambda imagePath: self.changeImage(imagePath))
		
		self.clickLabel = QtGui.QLabel("Teksti klikatessa")
		self.clickEdit = QtGui.QTextEdit()
		self.clickEdit.setMaximumHeight(50)
		self.clickEdit.focusOutEvent = lambda s: self.changeClickEdit()
		
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
		
	def changeNameEdit(self):
		self.parent.changeName(self.nameEdit, self.gameImageObject)
		
	def changeClickEdit(self):
		self.parent.changeExamineText(self.clickEdit, self.gameImageObject)
		
	def clearKey(self):
		self.gameObject.clearKey()
		
	def changeKey(self):
		keyObject = self.keyCombo.itemData(self.keyCombo.currentIndex())
		if (keyObject):
			self.gameObject.clearKey()
			
			# Set object's key to the object pointed by combobox
			self.gameObject.setKey(self.keyCombo.itemData(self.keyCombo.currentIndex()))
		else:
			return
		
	def changeLocked(self):
		if (self.lockedCheckbox.isChecked()):
			# TODO: Get imagePath better way (and clear airfreshener.png)
			self.gameObject.setLocked(True, "images/airfreshener.png")
			self.gameImageObject = self.gameObject.lockedImage
		else:
			self.gameObject.setLocked(False)
			self.gameImageObject = None
			self.nameEdit.setText("")
			self.clickEdit.setText("")
			
		self.setImage()
		self.setLocked()
		
	# Disable widget parts if checkbox says so
	def setLocked(self):
		notLocked = not self.lockedCheckbox.isChecked()
		self.nameLabel.setDisabled(notLocked)
		self.nameEdit.setDisabled(notLocked)
		self.keyLabel.setDisabled(notLocked)
		self.keyCombo.setDisabled(notLocked)
		self.image.setDisabled(notLocked)
		self.clickLabel.setDisabled(notLocked)
		self.clickEdit.setDisabled(notLocked)
		
	def changeImage(self, imagePath):
		self.parent.setObjectImage(imagePath, self.image)
		# TODO: Create image if doesn't exist!
		self.gameImageObject.setSource(imagePath)
		
	# Set the whole widget's enabled status
	def setDisabled(self, isDisabled):
		super(ObjectImageSettings, self).setDisabled(isDisabled)
		
		# If disabled, clear image and clear text fields
		if (isDisabled):
			self.gameImageObject = None
			self.setImage()
			self.nameEdit.setText("")
			self.clickEdit.setText("")
			
	def setImage(self):
		# Given gameImageObject may be None (no lockedImage, for example)
		if (self.gameImageObject):
			imagePath = self.parent.parent.getImageDir()+"/"+self.gameImageObject.getSource()
		elif self.objectType == "Door":
			imagePath = "images/door_placeholder.png"
		elif self.objectType == "Container":
			imagePath = "images/container_placeholder.png"
			
		# Ask parent to actually draw the image
		self.parent.setObjectImage(imagePath, self.image)
		
	def setSettings(self, gameObject, gameImageObject):
		self.gameObject = gameObject
		self.gameImageObject = gameImageObject
		self.objectType = self.gameObject.__class__.__name__
		
		# Set image
		self.setImage()
		
		# Change locked state
		if (self.canBeLocked):
			if (self.objectType == "Obstacle" or gameObject.isLocked()):
				self.lockedCheckbox.setCheckState(QtCore.Qt.CheckState.Checked)
			else:
				self.lockedCheckbox.setCheckState(QtCore.Qt.CheckState.Unchecked)
			self.setLocked()
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
		self.parent.setComboboxIndex(self.gameObject.key, self.keyCombo)
