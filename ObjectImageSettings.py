# -*- coding: UTF-8 -*-
from PySide import QtGui, QtCore
import localizer

DEBUG = True


# A widget that may have an object's closed, locked and open state settings
class ObjectImageSettings(QtGui.QWidget):

    def __init__(self, titleLabelText, nameLabelText,
                 canBeLocked=False, lockedText=None, parent=None):
        super(ObjectImageSettings, self).__init__(parent)

        if DEBUG:
            print("   [D] " + "ObjectImageSettings :: At ObjectImageSettings")

        self.layout = QtGui.QVBoxLayout()
        self.setLayout(self.layout)

        self.parent = parent

        self.labelLine = self.parent.createSeparator()
        self.titleLabel = QtGui.QLabel(titleLabelText)
        self.nameLabel = QtGui.QLabel(nameLabelText)
        self.nameEdit = QtGui.QLineEdit()
        self.nameEdit.focusOutEvent = lambda s: self.changeNameEdit()

        self.image = QtGui.QLabel(self)
        self.image.mousePressEvent =\
            lambda s: self.parent.showImageDialog(
                lambda imagePath: self.changeImage(imagePath))

        #self.clickLabel = QtGui.QLabel("Teksti klikatessa")
        self.clickLabel = QtGui.QLabel(localizer.translate(
            'ObjectImageSettings', 'textAsClicked'))
        self.clickEdit = QtGui.QTextEdit()
        self.clickEdit.setMaximumHeight(50)
        self.clickEdit.focusOutEvent = lambda s: self.changeClickEdit()

        self.layout.addWidget(self.labelLine)
        self.layout.addWidget(self.titleLabel)

        self.canBeLocked = canBeLocked
        if (self.canBeLocked):
            # TODO: Texts need to be set from outside
            self.lockedCheckbox = QtGui.QCheckBox(lockedText)
            self.lockedCheckbox.clicked.connect(self.changeLocked)
            self.keyLabel = QtGui.QLabel(
                localizer.translate('ObjectImageSettings', 'whatOpens'))
            self.keyCombo = self.parent.createCombobox()

            self.layout.addWidget(self.lockedCheckbox)
            self.layout.addWidget(self.keyLabel)
            self.layout.addWidget(self.keyCombo)

        self.layout.addWidget(self.nameLabel)
        self.layout.addWidget(self.nameEdit)
        self.layout.addWidget(self.image)
        self.layout.addWidget(self.clickLabel)
        self.layout.addWidget(self.clickEdit)

    def updateComboboxes(self, objectType):
        if DEBUG:
            print("   [D] " + "ObjectImageSettings :: At updateComboboxes")
        objectType = objectType.lower()
        if (objectType == "item"):
            self.parent.updateItemCombobox(
                self.keyCombo, localizer.translate(
                    'ObjectImageSettings', 'keyWasNotSelected'
                ), ("item",), ("item",), self.clearKey, self.changeKey
            )

    def changeNameEdit(self):
        if DEBUG:
            print("   [D] " + "ObjectImageSettings :: At changeNameEdit")
        self.parent.changeName(self.nameEdit, self.gameImageObject)

    def changeClickEdit(self):
        if DEBUG:
            print("   [D] " + "ObjectImageSettings :: At changeClickEdit")
        self.parent.changeExamineText(self.clickEdit, self.gameImageObject)

    def clearKey(self):
        if DEBUG:
            print("   [D] " + "ObjectImageSettings :: At clearKey")
        self.gameObject.clearKey()

    def changeKey(self):
        if DEBUG:
            print("   [D] " + "ObjectImageSettings :: At changeKey")
        keyObject = self.keyCombo.itemData(self.keyCombo.currentIndex())
        if (keyObject):
            self.gameObject.clearKey()

            # Set object's key to the object pointed by combobox
            self.gameObject.setKey(
                self.keyCombo.itemData(self.keyCombo.currentIndex()))
        else:
            return

    def changeLocked(self):
        if DEBUG:
            print("   [D] " + "ObjectImageSettings :: At changeLocked")
        if (self.lockedCheckbox.isChecked()):
            self.gameObject.setLocked(True)

            placeholder =\
                self.parent.editor.getPlaceholderImagePath(self.objectType)

            self.gameImageObject =\
                self.gameObject.lockedImage.placeholderImage.setSource(
                    self.parent.editor.editorImagePath+placeholder)
        else:
            self.gameObject.setLocked(False)
            self.keyCombo.setCurrentIndex(0)
            self.gameImageObject = None
            self.nameEdit.setText("")
            self.clickEdit.setText("")

        self.setImage()
        self.setLockedDisabled()

    # Disable widget parts if checkbox says so
    def setLockedDisabled(self):
        if DEBUG:
            print("   [D] " + "ObjectImageSettings :: At setLockedDisabled")
        notLocked = not self.lockedCheckbox.isChecked()
        self.nameLabel.setDisabled(notLocked)
        self.nameEdit.setDisabled(notLocked)
        self.keyLabel.setDisabled(notLocked)
        self.keyCombo.setDisabled(notLocked)
        self.image.setDisabled(notLocked)
        self.clickLabel.setDisabled(notLocked)
        self.clickEdit.setDisabled(notLocked)

    def changeImage(self, imagePath):
        if DEBUG:
            print("   [D] " + "ObjectImageSettings :: At changeImage")
        self.parent.setObjectImage(imagePath, self.image)
        self.gameImageObject.setSource(imagePath)
        self.parent.updateParent()
        self.parent.editor.updateSpaceTab()

    # Set the whole widget's enabled status
    def setDisabled(self, isDisabled):
        if DEBUG:
            print("   [D] " + "ObjectImageSettings :: At setDisabled")
        super(ObjectImageSettings, self).setDisabled(isDisabled)

        # If disabled, clear image and clear text fields
        if (isDisabled):
            self.gameImageObject = None
            self.setImage()
            self.nameEdit.setText("")
            self.clickEdit.setText("")

    def setImage(self):
        if DEBUG:
            print("   [D] " + "ObjectImageSettings :: At setImage")
        if (self.gameImageObject):
            imagePath =\
                self.gameImageObject.getRepresentingImage().absoluteImagePath
            self.parent.setObjectImage(imagePath, self.image)
        # Given gameImageObject may be None (no lockedImage, for example)
        elif self.objectType in ("Door", "Container", "Obstacle"):
            imagePath =\
                self.parent.editor.getPlaceholderImagePath(self.objectType)
            self.parent.setObjectImage(imagePath, self.image)

        # Ask parent to actually draw the image
        self.parent.setObjectImage(imagePath, self.image)

    def setSettings(self, gameObject, gameImageObject):
        if DEBUG:
            print("   [D] " + "ObjectImageSettings :: At setSettings")
        self.gameObject = gameObject
        self.gameImageObject = gameImageObject
        self.objectType = self.gameObject.__class__.__name__

        # Set image
        self.setImage()

        # Change locked state
        if (self.canBeLocked):
            if (gameObject.isLocked() or self.objectType == "Obstacle"):
                checked = QtCore.Qt.CheckState.Checked
            else:
                checked = QtCore.Qt.CheckState.Unchecked

            self.lockedCheckbox.setCheckState(checked)
            self.setLockedDisabled()
            self.setKey()

        # Delete checkbox if obstacle
        if (self.objectType == "Obstacle"):
            # Error about having already deleted may appear
            try:
                self.lockedCheckbox.deleteLater()
            except:
                pass

        self.parent.setObjectName(
            self.gameImageObject, self.gameObject.generalNameAdessive,
            self.nameEdit
        )
        self.parent.setExamineText(self.gameImageObject, self.clickEdit)

    # Set the correct key item in keyCombo
    def setKey(self):
        if DEBUG:
            print("   [D] " + "ObjectImageSettings :: At setKey")
        self.parent.setComboboxIndex(self.gameObject.key, self.keyCombo)
