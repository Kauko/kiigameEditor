from PySide import QtGui, QtCore
from ObjectImageSettings import ObjectImageSettings
from ImageCache import ImageCache
import localizer

# # TODO: remove useTypes[4], set it only in container instead
# # TODO: locked container is unfinished/buggy (Legendan kaappi)
# # TODO: Closed door image is buggy (Suihkun ovi, vessan ovi room2) (?)
# # TODO: Add ending checkbox to generic objects
# # TODO: Duplicate images when changing newly added image
# #     (copy generic attribute dict instead of using it as is)
# # TODO: Door state is initially closed even though should be open
# #     (Vessan ovi wc2)
# # TODO: Fix names in unnameable objects (start menu images)
# # TODO: Adding new sequence images is buggy
# #     (doesn't create new sequence entry in the object despite the image)
# # TODO: When removing sequence images remove the entry too
# # TODO: Hiuskeepperi has correct use target but no outcome
#       the poster_withglue is not listed in the outcome combobox
# # TODO: Old images/xxx_plceholder.png sources
# # TODO: Are new items added to comboboxes?
# # TODO: Removing view
# TODO: Save view texts too in addition to their objects
# # TODO: Adding new item from combo should focus on the new item?
# TODO: Click "All texts" button
# # TODO: Useless text in rooms (there should be combo too)
# TODO: Glow for different views
# TODO: Object types should be exactly as they are in the object!
# TODO: "X ei ole nimeä" common delegate

DEBUG = True


# Item and room settings widget used in editor
class SettingsWidget(QtGui.QWidget):

    def __init__(self, parent=None):
        super(SettingsWidget, self).__init__(parent)

        if DEBUG:
            print("   [D] " + "SettingsWidget :: At __init__")

        self.currentObject = None
        self.lastObjectType = None

       ## TODO: change to translation file
        self.useTypes = {
            0: localizer.translate('classSettingsWidget', 'noUse'),
            1: localizer.translate('classSettingsWidget', 'useToOtherObject'),
            2: localizer.translate('classSettingsWidget', 'openSth'),
            3: localizer.translate('classSettingsWidget', 'putSmwh'),
            4: localizer.translate('classSettingsWidget', 'deleteObstacle')
        }

        self.fadeTypes = {0: localizer.translate(
            'classSettingsWidget', 'instantly'), 1: localizer.translate(
            'classSettingsWidget', 'fade')}

        self.layout = QtGui.QVBoxLayout()
        self.setLayout(self.layout)

        self.setSizePolicy(QtGui.QSizePolicy(
            QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed))

        self.editor = parent
        self.imageCache = ImageCache()

        self.createOptionFields()

    def displayOptions(self, gameObject):
        if DEBUG:
            print("   [D] " + "SettingsWidget :: At displayOptions")
        self.currentObject = gameObject

        objectType = gameObject.__class__.__name__
        self.showWidgets(objectType)
        self.lastObjectType = objectType

        if (objectType == "Room"):
            self.setRoomOptions(gameObject)
        elif (objectType == "Sequence"):
            self.setSequenceOptions(gameObject)
        elif (objectType == "SequenceImage"):
            self.setSequenceImageOptions(gameObject)
        elif (objectType == "Start"):
            self.setStartOptions(gameObject)
        elif (objectType == "End"):
            self.setEndOptions(gameObject)
        elif (objectType == "Text"):
            self.setTextOptions(gameObject)
        elif (objectType == "Item"):
            self.setItemOptions(gameObject)
        elif (objectType == "Object"):
            self.setGenericOptions(gameObject)
        elif (objectType == "Door"):
            self.setDoorOptions(gameObject)
        elif (objectType == "Container"):
            self.setContainerOptions(gameObject)
        elif (objectType == "Obstacle"):
            self.setObstacleOptions(gameObject)
        elif (objectType == "JSONImage"):
            self.setJSONImageOptions(gameObject)
        elif (objectType == "MenuImage"):
            self.setJSONImageOptions(gameObject)
        elif (objectType == "BeginningImage"):
            self.setJSONImageOptions(gameObject)

    def showWidgets(self, objectType):
        if DEBUG:
            print("   [D] " + "SettingsWidget :: At showWidgets")
        if (self.lastObjectType):
            for item in self.itemSettings[self.lastObjectType]:
                item.hide()
        for item in self.itemSettings[objectType]:
            item.show()

    # Settings for the object view
    def createOptionFields(self):
        if DEBUG:
            print("   [D] " + "SettingsWidget :: At createOptionFields")
        # Name
        self.nameLabel = QtGui.QLabel(localizer.translate(
            'classSettingsWidget', 'name'))
        self.objectNameEdit = QtGui.QLineEdit()
        self.objectNameEdit.editingFinished.connect(self.changeName)

        # General image
        self.imgTextLabel = QtGui.QLabel(localizer.translate(
            'classSettingsWidget', 'image'))
        self.objectImage = QtGui.QLabel(self)
        self.objectImage.mousePressEvent =\
            lambda s: self.showImageDialog(self.changeObjectImage)

        self.useTextEdit = QtGui.QTextEdit()
        self.useTextEdit.setMaximumHeight(50)
        self.useTextEdit.focusOutEvent = lambda s: self.changeUseText()

        # Ending checkbox
        self.endingCheckbox = QtGui.QCheckBox()  # Set text afterwards
        self.endingCheckbox.setText(localizer.translate(
            'classSettingsWidget', 'gameEndsIfClicked'))
        self.endingCheckbox.stateChanged.connect(self.changeEndingCheckbox)

        # Music
        self.musicLabel = QtGui.QLabel(localizer.translate(
            'classSettingsWidget', 'music'))

        self.musicBtn = QtGui.QPushButton(localizer.translate(
            'classSettingsWidget', 'browse'), self)
        self.musicBtn.setToolTip(localizer.translate(
            'classSettingsWidget', 'chooseMusicFile'))
        self.musicBtn.resize(self.musicBtn.sizeHint())
        self.musicBtn.clicked.connect(
            lambda: self.showMusicDialog(self.changeMusic))

        self.musicTextEdit = QtGui.QLineEdit()
        self.musicTextEdit.setReadOnly(True)

        self.musicClear = QtGui.QPushButton(localizer.translate(
            'classSettingsWidget', 'noMusic'), self)
        self.musicClear.clicked.connect(self.clearMusic)

        # Where from dropdown box
        # self.whereFromLabel = QtGui.QLabel(
            # "Mistä kulkureiteistä tänne pääsee?")
        # TODO: whereFromCombo

        self.examineTextLabel = QtGui.QLabel(localizer.translate(
            'classSettingsWidget', 'textAsClicked'))
        self.examineTextEdit = QtGui.QTextEdit()
        self.examineTextEdit.setMaximumHeight(50)
        self.examineTextEdit.focusOutEvent = lambda s: self.changeExamineText()

        # Pickup text section
        self.pickupLabel = QtGui.QLabel(localizer.translate(
            'classSettingsWidget', 'picked'))
        self.pickupLabelLine = self.createSeparator()
        self.pickupLabelLine.setFrameStyle(
            QtGui.QFrame.HLine | QtGui.QFrame.Raised)
        self.pickupTextLabel = QtGui.QLabel(localizer.translate(
            'classSettingsWidget', 'textIfPicked'))

        self.pickupTextEdit = QtGui.QTextEdit()
        self.pickupTextEdit.setMaximumHeight(50)
        self.pickupTextEdit.focusOutEvent = lambda s: self.changePickupText()

        # Object usage
        self.useLabel = QtGui.QLabel(localizer.translate(
            'classSettingsWidget', 'usage'))
        self.useLabelLine = self.createSeparator()

        # Object type of usage
        self.useTypeCombo = QtGui.QComboBox(self)
        for i in self.useTypes:
            self.useTypeCombo.addItem(self.useTypes[i])
        self.useTypeCombo.activated.connect(self.changeItemUseType)

        self.useTextLabel = QtGui.QLabel(localizer.translate(
            'classSettingsWidget', 'textIfUsed'))

        # Use target
        self.useTargetCombo = self.createCombobox()
        self.updateUseTargetCombo()

        self.allTextsButton = QtGui.QPushButton(localizer.translate(
            'classSettingsWidget', 'theseAndOtherTexts'))
        self.allTextsButton.clicked.connect(self.showAllTexts)

        # Door widgets
        self.doorTransitionLabel = QtGui.QLabel(localizer.translate(
            'classSettingsWidget', 'whereItGoes'))
        self.doorTransitionCombo = self.createCombobox()
        self.updateDoorTransitionCombo()

        self.doorInitialStateLabel = QtGui.QLabel(localizer.translate(
            'classSettingsWidget', 'spaceAtStart'))
        self.doorInitialStateCombo = QtGui.QComboBox(self)
        self.doorInitialStateCombo.addItem(localizer.translate(
            'classSettingsWidget', 'shut'))
        self.doorInitialStateCombo.addItem(localizer.translate(
            'classSettingsWidget', 'open'))
        self.doorInitialStateCombo.activated.connect(
            lambda s: self.objectComboboxHandler(
                self.doorInitialStateCombo, self.changeDoorInitialState))

        self.openDoorImage = ObjectImageSettings(
            localizer.translate(
                'classSettingsWidget', 'openDoor'),
            localizer.translate('classSettingsWidget', 'openDoorName'),
            parent=self)
        self.closedDoorImage = ObjectImageSettings(
            localizer.translate(
                'classSettingsWidget', 'closedDoor'),
            localizer.translate(
                'classSettingsWidget', 'closedDoorName'),
            parent=self)
        self.lockedDoorImage = ObjectImageSettings(
            localizer.translate(
                'classSettingsWidget', 'lockedDoor'),
            localizer.translate(
                'classSettingsWidget', 'lockedDoorName'),
            True,
            localizer.translate('classSettingsWidget', 'locked'),
            parent=self)

        # Container widgets
        self.lockedContainerImage = ObjectImageSettings(
            localizer.translate(
                'classSettingsWidget', 'lockedContainer'),
            localizer.translate(
                'classSettingsWidget', 'lockedContainerName'),
            True,
            localizer.translate(
                'classSettingsWidget', 'locked'),
            parent=self)
        self.fullContainerImage = ObjectImageSettings(
            localizer.translate(
                'classSettingsWidget', 'openContainer'),
            localizer.translate(
                'classSettingsWidget', 'openContainerName'),
            parent=self)
        self.emptyContainerImage = ObjectImageSettings(
            localizer.translate(
                'classSettingsWidget', 'emptyContainer'),
            localizer.translate(
                'classSettingsWidget', 'emptyContainerName'),
            parent=self)

        # Obstacle widgets
        self.obstacleImage = ObjectImageSettings(
            None, localizer.translate(
                'classSettingsWidget', 'whatObstructs'),
            False, parent=self)
        self.obstacleBlocksLabel = QtGui.QLabel(localizer.translate(
            'classSettingsWidget', 'whatObstructs'))
        self.obstacleBlocksCombo = self.createCombobox()
        self.updateObstacleBlocksCombo()

        self.whatGoesLabel = QtGui.QLabel(localizer.translate(
            'classSettingsWidget', 'whatGoesToContainer'))
        self.whatGoesCombo = self.createCombobox()
        self.updateWhatGoesCombo()

        self.whatComesLabel = QtGui.QLabel(localizer.translate(
            'classSettingsWidget', 'whatComesFromContainer')
        )
        self.whatComesCombo = self.createCombobox()
        self.updateWhatComesCombo()

        self.useConsumeCheckbox = QtGui.QCheckBox()  # Set text afterwards
        self.useConsumeCheckbox.stateChanged.connect(self.changeUseConsume)

        self.outcomeLabel = QtGui.QLabel(localizer.translate(
            'classSettingsWidget', 'endResult')
        )
        self.outcomeCombobox = self.createCombobox()
        self.updateOutcomeCombobox()

        # Sequence
        self.sequenceTimeLabel = QtGui.QLabel(
            localizer.translate(
                'classSettingsWidget', 'imageShowTime'))
        self.sequenceTimeEdit = QtGui.QLineEdit()
        self.sequenceTimeEdit.setInputMask("9,9")
        self.sequenceTimeEdit.focusOutEvent =\
            lambda s: self.changeSequenceTime()

        self.sequenceFadeLabel = QtGui.QLabel(localizer.translate(
            'classSettingsWidget', 'fadeType'))
        self.sequenceFadeCombo = QtGui.QComboBox(self)
        for i in self.fadeTypes:
            self.sequenceFadeCombo.addItem(self.fadeTypes[i])
        self.sequenceFadeCombo.activated.connect(self.changeSequenceFadeCombo)

        # End
        self.textObjectTextLabel = QtGui.QLabel(localizer.translate(
            'classSettingsWidget', 'text'))
        self.textObjectTextEdit = QtGui.QLineEdit()
        self.textObjectTextEdit.focusOutEvent =\
            lambda s: self.changeTextObjectText()

        self.layout.addWidget(self.textObjectTextLabel)
        self.layout.addWidget(self.textObjectTextEdit)

        self.layout.addWidget(self.nameLabel)
        self.layout.addWidget(self.objectNameEdit)
        self.layout.addWidget(self.imgTextLabel)
        self.layout.addWidget(self.objectImage)

        self.layout.addWidget(self.musicLabel)
        self.layout.addWidget(self.musicTextEdit)
        self.layout.addWidget(self.musicBtn)
        self.layout.addWidget(self.musicClear)
        #self.layout.addWidget(self.whereFromLabel)

        self.layout.addWidget(self.endingCheckbox)

        self.layout.addWidget(self.examineTextLabel)
        self.layout.addWidget(self.examineTextEdit)
        self.layout.addWidget(self.pickupLabelLine)
        self.layout.addWidget(self.pickupLabel)
        self.layout.addWidget(self.pickupTextLabel)
        self.layout.addWidget(self.pickupTextEdit)

        self.layout.addWidget(self.useLabelLine)
        self.layout.addWidget(self.useLabel)
        self.layout.addWidget(self.useTypeCombo)
        self.layout.addWidget(self.useTargetCombo)

        self.layout.addWidget(self.useConsumeCheckbox)
        self.layout.addWidget(self.outcomeLabel)
        self.layout.addWidget(self.outcomeCombobox)

        self.layout.addWidget(self.useTextLabel)
        self.layout.addWidget(self.useTextEdit)
        self.layout.addWidget(self.allTextsButton)

        #self.layout.addWidget(self.doorTransitionLabelLine)
        self.layout.addWidget(self.doorTransitionLabel)
        self.layout.addWidget(self.doorTransitionCombo)

        self.layout.addWidget(self.doorInitialStateLabel)
        self.layout.addWidget(self.doorInitialStateCombo)

        self.layout.addWidget(self.openDoorImage)
        self.layout.addWidget(self.lockedDoorImage)
        self.layout.addWidget(self.closedDoorImage)

        self.layout.addWidget(self.whatGoesLabel)
        self.layout.addWidget(self.whatGoesCombo)
        self.layout.addWidget(self.whatComesLabel)
        self.layout.addWidget(self.whatComesCombo)

        self.layout.addWidget(self.fullContainerImage)
        self.layout.addWidget(self.lockedContainerImage)
        self.layout.addWidget(self.emptyContainerImage)

        self.layout.addWidget(self.obstacleBlocksLabel)
        self.layout.addWidget(self.obstacleBlocksCombo)
        self.layout.addWidget(self.obstacleImage)

        self.layout.addWidget(self.sequenceTimeLabel)
        self.layout.addWidget(self.sequenceTimeEdit)
        self.layout.addWidget(self.sequenceFadeLabel)
        self.layout.addWidget(self.sequenceFadeCombo)

        # Removebuttons
        self.removeObjectButton = QtGui.QPushButton(
            localizer.translate(
                'classSettingsWidget', 'removeObject'))
        self.layout.addWidget(self.removeObjectButton)
        self.removeObjectButton.clicked.connect(lambda: self.removeObject())
        self.removeViewButton = QtGui.QPushButton(
            localizer.translate(
                'classSettingsWidget', 'removeView'))
        self.layout.addWidget(self.removeViewButton)
        self.removeViewButton.clicked.connect(lambda: self.removeView())

        # Which widgets are shown with each object
        self.itemSettings = {
            "Room": [
                self.imgTextLabel,
                self.objectImage,
                self.nameLabel,
                self.objectNameEdit,
                self.musicLabel,
                self.musicTextEdit,
                self.musicBtn,
                self.musicClear,
                self.removeViewButton
                #self.whereFromLabel
                # TODO: doorCombo for "where from" values
            ],
            "Sequence": [
                self.nameLabel,
                self.objectNameEdit,
                self.musicLabel,
                self.musicTextEdit,
                self.musicBtn,
                self.musicClear,
                self.removeViewButton
            ],
            "SequenceImage": [
                self.imgTextLabel,
                self.objectImage,
                self.sequenceTimeLabel,
                self.sequenceTimeEdit,
                self.sequenceFadeLabel,
                self.sequenceFadeCombo,
                self.removeViewButton
            ],
            "End": [
                self.imgTextLabel,
                self.objectImage,
                self.nameLabel,
                self.objectNameEdit,
                self.musicLabel,
                self.musicTextEdit,
                self.musicBtn,
                self.musicClear,
            ],
            "Text": [
                self.textObjectTextLabel,
                self.textObjectTextEdit
            ],
            "BeginningImage": [
                self.imgTextLabel,
                self.objectImage,
            ],
            "JSONImage": [
                self.imgTextLabel,
                self.objectImage,
            ],
            "Start": [
                self.musicLabel,
                self.musicTextEdit,
                self.musicBtn,
                self.musicClear,
            ],
            "MenuImage": [
                self.imgTextLabel,
                self.objectImage,
            ],
            "Item": [
                self.nameLabel,
                self.objectNameEdit,
                self.imgTextLabel,
                self.objectImage,
                self.examineTextLabel,
                self.examineTextEdit,
                self.pickupLabelLine,
                self.pickupLabel,
                self.pickupTextLabel,
                self.pickupTextEdit,
                self.useLabelLine,
                self.useLabel,
                self.useTypeCombo,
                self.useTargetCombo,
                self.useTextLabel,
                self.useTextEdit,
                self.allTextsButton,
                self.useConsumeCheckbox,
                self.outcomeLabel,
                self.outcomeCombobox,
                self.removeObjectButton
            ],
            "Object": [
                self.nameLabel,
                self.objectNameEdit,
                self.imgTextLabel,
                self.objectImage,
                self.endingCheckbox,
                self.examineTextLabel,
                self.examineTextEdit,
                self.removeObjectButton
            ],
            "Door": [
                #self.doorTransitionLabelLine,
                self.doorTransitionLabel,
                self.doorTransitionCombo,

                self.doorInitialStateLabel,
                self.doorInitialStateCombo,

                self.openDoorImage,
                self.closedDoorImage,
                self.lockedDoorImage,
                self.removeObjectButton
            ],
            "Container": [
                self.lockedContainerImage,
                self.fullContainerImage,
                self.emptyContainerImage,

                self.whatGoesLabel,
                self.whatGoesCombo,
                self.whatComesLabel,
                self.whatComesCombo,
                self.removeObjectButton
            ],
            "Obstacle": [
                self.obstacleImage,
                self.obstacleBlocksLabel,
                self.obstacleBlocksCombo,
                self.removeObjectButton
            ]
        }

        # Hide every widget
        for key in self.itemSettings:
            for item in self.itemSettings[key]:
                item.hide()

    # Update comboboxes having objectType objects
    def updateComboboxes(self, objectType):
        if DEBUG:
            print("   [D] " + "SettingsWidget :: At updateComboboxes")
        objectType = objectType.lower()
        if (objectType == "room"):
            self.updateDoorTransitionCombo()
        elif (objectType == "door"):
            self.updateObstacleBlocksCombo()
        elif (objectType == "item"):
            self.updateWhatGoesCombo()
            self.updateWhatComesCombo()
            self.updateOutcomeCombobox()
        elif (objectType == "object"):
            self.updateOutcomeCombobox()

        # Update every time
        self.updateUseTargetCombo()

        # Update other widgets
        self.lockedDoorImage.updateComboboxes(objectType)
        self.lockedContainerImage.updateComboboxes(objectType)

    def updateUseTargetCombo(self):
        if DEBUG:
            print("   [D] " + "SettingsWidget :: At updateUseTargetCombo")
        self.updateItemCombobox(
            self.useTargetCombo, localizer.translate(
                'classSettingsWidget', 'notSelected'),
            connectTo=self.changeUseTarget)

    def updateDoorTransitionCombo(self):
        if DEBUG:
            print("   [D] " + "SettingsWidget :: At updateDoorTransitionCombo")
        self.updateItemCombobox(
            self.doorTransitionCombo, localizer.translate(
                'classSettingsWidget', 'notAnywhere'),
            "room", connectTo=self.changeDoorTransition)

    def updateObstacleBlocksCombo(self):
        if DEBUG:
            print("   [D] " + "SettingsWidget :: At updateObstacleBlocksCombo")
        self.updateItemCombobox(
            self.obstacleBlocksCombo, localizer.translate(
                'classSettingsWidget', 'noNothing'), ("door",), ("door",),
            noChoiceMethod=self.clearObstacleBlock,
            connectTo=self.changeObstacleBlock)

    def updateWhatGoesCombo(self):
        if DEBUG:
            print("   [D] " + "SettingsWidget :: At updateWhatGoesCombo")
        self.updateItemCombobox(
            self.whatGoesCombo, localizer.translate(
                'classSettingsWidget', 'notAnything'),
            ("item",), ("item",),
            connectTo=self.changeWhatGoes)

    def updateWhatComesCombo(self):
        if DEBUG:
            print("   [D] " + "SettingsWidget :: At updateWhatComesCombo")
        self.updateItemCombobox(
            self.whatComesCombo, localizer.translate(
                'classSettingsWidget', 'noNothing'),
            ("item",), ("item",),
            connectTo=self.changeWhatComes)

    def updateOutcomeCombobox(self):
        if DEBUG:
            print("   [D] " + "SettingsWidget :: At updateOutcomeCombobox")
        self.updateItemCombobox(
            self.outcomeCombobox, localizer.translate(
                'classSettingsWidget', 'notSelected'),
            ("object", "item"), ("object", "item"),
            noChoiceMethod=self.clearOutcome,
            connectTo=self.changeOutcome)

    def changeSequenceTime(self):
        if DEBUG:
            print("   [D] " + "SettingsWidget :: At changeSequenceTime")
        time = int(float(self.sequenceTimeEdit.text().replace(",", "."))*1000)
        self.currentObject.setShowTime(time)

    def changeSequenceFadeCombo(self):
        if DEBUG:
            print("   [D] " + "SettingsWidget :: At changeSequenceFadeCombo")
        doFade = (self.sequenceFadeCombo.currentIndex() is True)
        self.currentObject.setDoFade(doFade)

    def changeTextObjectText(self):
        if DEBUG:
            print("   [D] " + "SettingsWidget :: At changeTextObjectText")
        self.currentObject.setText(self.textObjectTextEdit.text())

    def changeEndingCheckbox(self):
        if DEBUG:
            print("   [D] " + "SettingsWidget :: At changeEndingCheckbox")
        self.currentObject.setIsEnding(self.endingCheckbox.isChecked())

    # Start menu
    def setStartOptions(self, startObject):
        if DEBUG:
            print("   [D] " + "SettingsWidget :: At setStartOptions")
        # Start music
        self.setObjectMusic(startObject)

    # End view
    def setEndOptions(self, endObject):
        if DEBUG:
            print("   [D] " + "SettingsWidget :: At setEndOptions")
        # End name
        self.setObjectName(overrideText=endObject.generalName)

        # End image
        self.setObjectImage(
            endObject.getRepresentingImage().getRepresentingImage()
            .absoluteImagePath)

    # Text object
    def setTextOptions(self, textObject):
        if DEBUG:
            print("   [D] " + "SettingsWidget :: At setTextOptions")
        self.textObjectTextEdit.setText(textObject.getText())

    # Set either currentObject or the given object's music
    def setObjectMusic(self, gameObject=None):
        if DEBUG:
            print("   [D] " + "SettingsWidget :: At setObjectMusic")
        if not (gameObject):
            gameObject = self.currentObject

        # Music may return None which doesn't have split
        try:
            music = gameObject.getMusic().split("/")[-1]
        except AttributeError:
            music = ""
        self.musicTextEdit.setText(music)

    # Generic JSON images
    def setJSONImageOptions(self, imageObject):
        if DEBUG:
            print("   [D] " + "SettingsWidget :: At setJSONImageOptions")
        # Image
        self.setObjectImage(
            imageObject.getRepresentingImage()
            .getRepresentingImage().absoluteImagePath)

    # Set the input field values for rooms
    def setRoomOptions(self, room):
        if DEBUG:
            print("   [D] " + "SettingsWidget :: At setRoomOptions")
        # Room name
        self.setObjectName(room, room.generalName)

        # Room background
        self.setObjectImage(
            room.getRepresentingImage()
            .getRepresentingImage().absoluteImagePath)

        # Room music
        self.setObjectMusic(room)

    def setSequenceOptions(self, sequence):
        if DEBUG:
            print("   [D] " + "SettingsWidget :: At setSequenceOptions")
        # Sequence name
        self.setObjectName(sequence, sequence.generalNameAdessive)

        # Sequence background
        self.setObjectImage(
            sequence.getRepresentingImage()
            .getRepresentingImage().absoluteImagePath)

        # Sequence music
        self.setObjectMusic(sequence)

    def setSequenceImageOptions(self, sequenceImage):
        if DEBUG:
            print("   [D] " + "SettingsWidget :: At setSequenceImageOptions")
        # Image
        self.setObjectImage(
            sequenceImage.getRepresentingImage()
            .getRepresentingImage().absoluteImagePath)

        # Set image display time. Convert into str and replace dots
        showTime = self.currentObject.getShowTime()
        if (showTime):
            time = str(showTime/1000).replace(".", ",")
        else:
            time = "0,0"
        self.sequenceTimeEdit.setText(time)

        # Image fade type
        doFade = self.currentObject.getDoFade()
        if not (doFade):
            doFade = False
        self.sequenceFadeCombo.setCurrentIndex(doFade)

    # Set the input field values for items
    def setItemOptions(self, item):
        if DEBUG:
            print("   [D] " + "SettingsWidget :: At setItemOptions")
        imageObject = item.getRepresentingImage().getRepresentingImage()

        # Object name
        self.setObjectName(imageObject, item.generalNameAdessive)

        # Item image
        self.setObjectImage(imageObject.absoluteImagePath)

        # Examine text
        self.setExamineText(self.currentObject)

        # Pickup text
        pickupText = item.getPickupText()
        if not (pickupText):
            pickupText = ""
        self.pickupTextEdit.setText(pickupText)

        # Use type of the item
        itemTarget = self.editor.getItemUse(item)
        itemTargetType = itemTarget.__class__.__name__
        useType = 0

        if (itemTargetType in ("Object", "Item")):
            useType = 1
        elif (itemTargetType == "Obstacle"):
            useType = 5
        elif (itemTargetType in ("Door", "Container")):
            # Item may unlock door or container or may go into a container
            if (itemTarget.key == item):
                useType = 2
            else:
                try:
                    if (itemTarget.inItem == item):
                        useType = 3
                except AttributeError:
                    pass

        self.setUseConsume()

        self.setItemUseType(useType)
        self.setItemUseTarget(itemTarget)
        self.setItemOutcome(self.currentObject.outcome)
        self.setUseText()

    # Set the input field values for generic objects
    def setGenericOptions(self, genericObject):
        if DEBUG:
            print("   [D] " + "SettingsWidget :: At setGenericOptions")
        # Object name
        self.setObjectName(genericObject, genericObject.generalNameAdessive)

        # Object image
        imageObject = genericObject.getRepresentingImage()\
            .getRepresentingImage()
        self.setObjectImage(imageObject.absoluteImagePath)

        # Ending
        if (self.currentObject.getIsEnding()):
            self.endingCheckbox.setCheckState(QtCore.Qt.CheckState.Checked)
        else:
            self.endingCheckbox.setCheckState(QtCore.Qt.CheckState.Unchecked)

        # Examine text
        self.setExamineText(self.currentObject)

    # Set the input field values for containers
    def setContainerOptions(self, container):
        if DEBUG:
            print("   [D] " + "SettingsWidget :: At setContainerOptions")
        # Set image settings for each image
        self.fullContainerImage.setSettings(container, container.fullImage)
        self.lockedContainerImage.setSettings(container, container.lockedImage)
        self.emptyContainerImage.setSettings(container, container.emptyImage)

        # Set what goes, what comes from the container
        self.setComboboxIndex(container.inItem, self.whatGoesCombo)
        self.setComboboxIndex(container.outItem, self.whatComesCombo)

    # Set the input field values for obstacles
    def setObstacleOptions(self, obstacle):
        if DEBUG:
            print("   [D] " + "SettingsWidget :: At setObstacleOptions")
        self.obstacleImage.setSettings(obstacle, obstacle.blockingImage)

    def setObjectImage(self, imagePath, objectImage=None):
        if DEBUG:
            print("   [D] " + "SettingsWidget :: At setObjectImage")
        imgPixmap = self.imageCache.createPixmap(imagePath)

        # TODO: Have spacing for smaller items
        if (imgPixmap.size().height() > 200):
            imgPixmap = imgPixmap.scaled(200, 200, QtCore.Qt.KeepAspectRatio)

        if (objectImage):
            objectImage.setPixmap(imgPixmap)
        else:
            self.objectImage.setPixmap(imgPixmap)

    # Set item use type
    def setItemUseType(self, typeIndex):
        if DEBUG:
            print("   [D] " + "SettingsWidget :: At setItemUseType")
        self.useTypeCombo.setCurrentIndex(typeIndex)

        self.updateUseTargetCombobox(typeIndex, self.useTargetCombo)

        # Show extra options when selecting use on other object
        if (typeIndex == 1):
            self.useConsumeCheckbox.setText(
                localizer.translate(
                    'classSettingsWidget', 'vanishDuringUse')
            )
            self.useConsumeCheckbox.show()
            self.outcomeLabel.show()
            self.outcomeCombobox.show()
        else:
            self.useConsumeCheckbox.hide()
            self.outcomeLabel.hide()
            self.outcomeCombobox.hide()

        # When no use, hide and clear elements
        if (typeIndex == 0):
            self.useTargetCombo.hide()
            self.useTextLabel.hide()
            self.useTextEdit.hide()
            self.useTextEdit.clear()
            self.changeUseText()
            self.allTextsButton.hide()

            self.currentObject.clearTarget()
        else:
            self.useTargetCombo.show()
            self.useTextLabel.show()
            self.useTextEdit.show()
            self.allTextsButton.show()

    #  Set item use target
    def setItemUseTarget(self, useItem):
        if DEBUG:
            print("   [D] " + "SettingsWidget :: At setItemUseTarget")
        if (useItem):
            # Find the combobox item with the given item
            for i in range(self.useTargetCombo.count()):
                if (self.useTargetCombo.itemData(i) == useItem):
                    self.useTargetCombo.setCurrentIndex(i)
                    return
        self.useTargetCombo.setCurrentIndex(0)

    def setItemOutcome(self, outcomeItem):
        if DEBUG:
            print("   [D] " + "SettingsWidget :: At setItemOutcome")
        if (outcomeItem):
            # Find the combobox item with the given item
            for i in range(self.outcomeCombobox.count()):
                if (self.outcomeCombobox.itemData(i) == outcomeItem):
                    self.outcomeCombobox.setCurrentIndex(i)
                    return

        self.outcomeCombobox.setCurrentIndex(0)

    def setDoorInitialState(self):
        if DEBUG:
            print("   [D] " + "SettingsWidget :: At setDoorInitialState")
        # Door open
        if (self.currentObject.closedImage or self.currentObject.lockedImage):
            self.doorInitialStateCombo.setCurrentIndex(0)
        # Door closed
        else:
            self.doorInitialStateCombo.setCurrentIndex(1)

        self.changeDoorInitialState()

    def setDoorOptions(self, doorObject):
        if DEBUG:
            print("   [D] " + "SettingsWidget :: At setDoorOptions")
        # Set each image's settings
        self.closedDoorImage.setSettings(doorObject, doorObject.closedImage)
        self.lockedDoorImage.setSettings(doorObject, doorObject.lockedImage)
        self.openDoorImage.setSettings(doorObject, doorObject.openImage)

        # Door transition room
        self.setComboboxIndex(doorObject.transition, self.doorTransitionCombo)

        # Set door open or closed in the beginning
        self.setDoorInitialState()

    # Set use item for items
    def setUseText(self, textEdit=None, item=None):
        if DEBUG:
            print("   [D] " + "SettingsWidget :: At setUseText")
        if (self.useTypeCombo.currentIndex() == 0):
            return

        if not (item):
            item = self.currentObject

        useText = item.getUseText()
        if not (useText):
            useText = ""

        if (textEdit):
            textEdit.setText(useText)
        else:
            self.useTextEdit.setText(useText)

    # Set examine text for the given object
    def setExamineText(self, gameObject, textEdit=None):
        if DEBUG:
            print("   [D] " + "SettingsWidget :: At setExamineText")
        try:
            text = gameObject.getExamineText()
        except AttributeError:
            text = ""

        if (textEdit):
            textEdit.setText(text)
        else:
            self.examineTextEdit.setText(text)

    # Set any game object name
    def setObjectName(self, gameObject=None, textStart="Object",
                      textEdit=None, overrideText=None):
        if DEBUG:
            print("   [D] " + "SettingsWidget :: At setObjectName")
        if not (gameObject):
            gameObject = self.currentObject

        if (overrideText):
            name = overrideText
        else:
            # Given image may be None
            try:
                name = gameObject.getName()
            except AttributeError:
                name = ""

            if (name is None):
                name = localizer.translate(
                    'classSettingsWidget', 'objectHasNoName')

        # If textEdit is defined, set its text instead
        if (textEdit):
            textEdit.setText(name)
        else:
            self.objectNameEdit.setText(name)

    def setUseConsume(self):
        if DEBUG:
            print("   [D] " + "SettingsWidget :: At setUseConsume")
        isConsumed = self.useConsumeCheckbox.isChecked()
        self.currentObject.setConsume(isConsumed)

        if (isConsumed):
            self.useConsumeCheckbox.setCheckState(QtCore.Qt.CheckState.Checked)
        else:
            self.useConsumeCheckbox.setCheckState(
                QtCore.Qt.CheckState.Unchecked)

    def changeWhereLocated(self, combobox):
        if DEBUG:
            print("   [D] " + "SettingsWidget :: At changeWhereLocated")
        # What is this used for?
        print("Change where located to", combobox.itemData(
            combobox.currentIndex()))

    # Text that comes after using an item
    def changeUseText(self):
        if DEBUG:
            print("   [D] " + "SettingsWidget :: At changeUseText")
        # TODO: Disable text field if no target is selected

        self.currentObject.setUseText(
            self.useTextEdit.toPlainText())

    def changePickupText(self):
        if DEBUG:
            print("   [D] " + "SettingsWidget :: At changePickupText")
        self.currentObject.setPickupText(self.pickupTextEdit.toPlainText())

    def changeExamineText(self, textEdit=None, gameObject=None):
        if DEBUG:
            print("   [D] " + "SettingsWidget :: At changeExamineText")
        if not (gameObject):
            gameObject = self.currentObject

        if not (textEdit):
            textEdit = self.examineTextEdit

        gameObject.setExamineText(textEdit.toPlainText())

    def changeDoorInitialState(self):
        if DEBUG:
            print("   [D] " + "SettingsWidget :: At changeDoorInitialState")
        # Initially closed, all states (closed, locked, open) are possible
        if (self.doorInitialStateCombo.currentIndex() == 0):
            self.closedDoorImage.setDisabled(False)
            self.lockedDoorImage.setDisabled(False)
            self.openDoorImage.setDisabled(False)

            # Add door's closed image
            self.currentObject.setClosed(True)
            self.currentObject.closedImage.placeholderImage.setSource(
                self.editor.getPlaceholderImagePath("Door"))

        # Initially open, only "open" state is possible
        else:
            self.closedDoorImage.setDisabled(True)
            self.lockedDoorImage.setDisabled(True)
            self.openDoorImage.setDisabled(False)

            # Remove door's closed and locked images
            self.currentObject.setClosed(False)
            self.currentObject.setLocked(False)

    # Change the image of a gameobject
    def changeObjectImage(self, imagePath, image=None, gameObject=None):
        if DEBUG:
            print("   [D] " + "SettingsWidget :: At changeObjectImage")
        # If no image, a default image var will be used
        # TODO: Copy the chosen image to the 'images' folder of the scenario?
        self.currentObject.getRepresentingImage().setSource(imagePath)
        self.setObjectImage(imagePath, image)
        print(imagePath)

        if not (gameObject):
            gameObject = self.currentObject

        self.editor.drawRoomItems()
        self.updateParent()
        self.editor.updateSpaceTab()

    # Change music
    def changeMusic(self, imagePath):
        if DEBUG:
            print("   [D] " + "SettingsWidget :: At changeMusic")
        self.currentObject.setMusic(imagePath)

    def changeUseConsume(self):
        if DEBUG:
            print("   [D] " + "SettingsWidget :: At changeUseConsume")
        self.currentObject.setConsume(self.useConsumeCheckbox.isChecked())

    def changeOutcome(self):
        if DEBUG:
            print("   [D] " + "SettingsWidget :: At changeOutcome")
        self.currentObject.setOutcome(
            self.outcomeCombobox.itemData(self.outcomeCombobox.currentIndex()))

    def clearOutcome(self):
        if DEBUG:
            print("   [D] " + "SettingsWidget :: At clearOutcome")
        self.currentObject.setOutcome(None)

    def clearUseTarget(self):
        if DEBUG:
            print("   [D] " + "SettingsWidget :: At clearUseTarget")
        # TODO: This is run even when populating the combobox
        #self.currentObject.clearTarget()

    def changeObstacleBlock(self):
        if DEBUG:
            print("   [D] " + "SettingsWidget :: At changeObstacleBlock")
        self.currentObject.setBlockTarget(
            self.obstacleBlocksCombo.itemData(
                self.obstacleBlocksCombo.currentIndex()))

    def clearObstacleBlock(self):
        if DEBUG:
            print("   [D] " + "SettingsWidget :: At clearObstacleBlock")
        self.currentObject.clearBlockTarget()

    def changeWhatGoes(self):
        if DEBUG:
            print("   [D] " + "SettingsWidget :: At changeWhatGoes")
        self.currentObject.setInItem(
            self.whatGoesCombo.itemData(self.whatGoesCombo.currentIndex()))

    def clearWhatGoes(self):
        if DEBUG:
            print("   [D] " + "SettingsWidget :: At clearWhatGoes")
        self.currentObject.clearInItem()

    def changeWhatComes(self):
        if DEBUG:
            print("   [D] " + "SettingsWidget :: At changeWhatComes")
        self.currentObject.setOutItem(
            self.whatComesCombo.itemData(
                self.whatComesCombo.currentIndex()))

    def clearWhatComes(self):
        if DEBUG:
            print("   [D] " + "SettingsWidget :: At clearWhatComes")
        self.currentObject.clearOutItem()

    def changeDoorTransition(self):
        if DEBUG:
            print("   [D] " + "SettingsWidget :: At changeDoorTransition")
        self.currentObject.setTransition(
            self.doorTransitionCombo.itemData(
                self.doorTransitionCombo.currentIndex()))

    def changeName(self, textEdit=None, gameObject=None):

        if DEBUG:
            print("   [D] " + "SettingsWidget :: At changeName")

        if not (gameObject):
            gameObject = self.currentObject

        if (textEdit):
            text = textEdit.text()
        else:
            text = self.objectNameEdit.text()

        if (len(text) == 0):
            text = localizer.translate(
                'classSettingsWidget', 'objectHasNoName')

        gameObject.setName(text)
        self.updateParent()

    # Update parent tab elements
    def updateParent(self):
        if DEBUG:
            print("   [D] " + "SettingsWidget :: At updateParent")
        if (self.currentObject.__class__.__name__ in ("Room", "Sequence")):
            self.editor.drawRooms()
        else:
            self.editor.drawRoomItems()

    # Change object use type
    def changeItemUseType(self, index):
        if DEBUG:
            print("   [D] " + "SettingsWidget :: At changeItemUseType")
        self.setItemUseType(index)
        self.setItemUseTarget(None)
        self.setItemOutcome(None)

    # Set item use target
    def changeUseTarget(self):
        if DEBUG:
            print("   [D] " + "SettingsWidget :: At changeUseTarget")
        index = self.useTargetCombo.currentIndex()

        targetType = self.useTargetCombo.itemData(index).__class__.__name__
        selectedObject = self.useTargetCombo.itemData(index)

        objectRole = 0
        useType = self.useTypeCombo.currentIndex()
        if (targetType in ("Door", "Container")):
            # Unlock something and target object is not set into locked state
            if (useType == 2):
                # TODO: Really nullify old key?
                # Get old current object's key and nullify it
                self.currentObject.clearTarget()

                # Nullify selected door's key
                if (self.useTargetCombo.itemData(index).key):
                    self.useTargetCombo.itemData(index).key.clearTarget()

                # Set the object to be locked with new key
                imagePath = self.editor.getPlaceholderImagePath(targetType)
                selectedObject.setLocked(True, imagePath, self.currentObject)

            # Put into container
            elif (useType == 3):
                objectRole = 1

            # Get from container
            #elif (useType == 4):
            #   objectRole = 2

        self.currentObject.setTargetObject(selectedObject, objectRole)
        self.setUseText()

    # Create new game object
    def createObject(self, objectType):
        if DEBUG:
            print("   [D] " + "SettingsWidget :: At createObject")
        self.editor.createObject(objectType)
        self.updateComboboxes(objectType)

    def removeObject(self):
        if DEBUG:
            print("   [D] " + "SettingsWidget :: At removeObject")
        self.editor.removeObjectsButtonClicked()

    def removeView(self):
        if DEBUG:
            print("   [D] " + "SettingsWidget :: At removeView")
        self.editor.removeViewsButtonClicked()

    def showAllTexts(self):
        if DEBUG:
            print("   [D] " + "SettingsWidget :: At showAllTexts")
        # TODO: Select the actual object
        self.editor.tabWidget.setCurrentIndex(2)
        #self.currentObject.

    def clearMusic(self):
        if DEBUG:
            print("   [D] " + "SettingsWidget :: At clearMusic")
        self.currentObject.clearMusic()
        self.musicTextEdit.clear()

    # Sets the index of a combobox according to given targetObject
    def setComboboxIndex(self, targetObject, combobox):
        if DEBUG:
            print("   [D] " + "SettingsWidget :: At setComboboxIndex")
        # Find the combobox item with the given item
        for i in range(combobox.count()):
            if (combobox.itemData(i) == targetObject):
                combobox.setCurrentIndex(i)
                return
        combobox.setCurrentIndex(0)

    # Create and return a plain combobox
    def createCombobox(self):
        if DEBUG:
            print("   [D] " + "SettingsWidget :: At createCombobox")
        combobox = QtGui.QComboBox(self)
        combobox.setIconSize(QtCore.QSize(50, 50))
        return combobox

    # Create combobox from given items with default of all item types
    def updateItemCombobox(self, combobox, noChoiceText, objectTypes=None,
                           addChoices=None, noChoiceMethod=None,
                           connectTo=None):
        if DEBUG:
            print("   [D] " + "SettingsWidget :: At updateItemCombobox")
        if not (objectTypes):
            objectTypes = ("object", "item", "door", "container", "obstacle")

        if (objectTypes == "room"):
            self.populateRoomCombobox(combobox, addChoices)
        else:
            self.populateCombobox(
                objectTypes, combobox, noChoiceText, addChoices,
                noChoiceMethod)
        combobox.activated.connect(
            lambda s: self.objectComboboxHandler(combobox, connectTo))

        return combobox

    # Populate a given combobox with game rooms
    def populateRoomCombobox(self, combobox, addChoice=True):
        if DEBUG:
            print("   [D] " + "SettingsWidget :: At populateRoomCombobox")
        if (addChoice):
            imgPixmap = self.imageCache.createPixmap(self.editor.newIconPath)
            combobox.addItem(imgPixmap, localizer.translate(
                'classSettingsWidget', 'addRoom'))

        for room in self.editor.getRoomObjects():
            # TODO model to eliminate redundancy from getName/roomName patterns
            roomName = room.getName()
            if not (roomName):
                roomName = localizer.translate(
                    'classSettingsWidget', 'roomHasNoName')
            imgPixmap = self.imageCache.createPixmap(
                room.getRepresentingImage().getRepresentingImage()
                .absoluteImagePath)

            roomIcon = QtGui.QIcon(imgPixmap)
            combobox.addItem(roomIcon, roomName, userData=room)

    # Create use target combobox
    def updateUseTargetCombobox(self, useType, combobox):
        if DEBUG:
            print("   [D] " + "SettingsWidget :: At updateUseTargetCombobox")
        if (useType == 0):
            objectTypes = ()
        elif (useType == 1):
            objectTypes = ("item", "object")
        elif (useType == 2):
            objectTypes = ("door", "container")
        elif (useType == 3):
            objectTypes = ("container",)
        elif (useType == 4):
            objectTypes = ("obstacle",)

        self.populateCombobox(
            objectTypes, combobox, localizer.translate(
                'classSettingsWidget', 'notSelected'),
            objectTypes, self.clearUseTarget)

    # Handle item combobox item choosing callback
    def objectComboboxHandler(self, combobox, callback):
        if DEBUG:
            print("   [D] " + "SettingsWidget :: At objectComboboxHandler")
        target = combobox.itemData(combobox.currentIndex())
        targetType = target.__class__.__name__

        # If chosen item is something else than a game object don't do callback
        if (targetType == "method"):
            target()
        elif (targetType == "str"):
            self.createObject(target)
        else:
            callback()

    # Populate a given combobox with given types of objects
    # categorized by game rooms
    def populateCombobox(self, objectTypes, combobox, noChoiceText=None,
                         addChoices=None, noChoiceMethod=None):
        if DEBUG:
            print("   [D] " + "SettingsWidget :: At populateRoomCombobox")
        combobox.clear()

        itemCounter = 0

        # Add the given string as the first item
        if (noChoiceText):
            imgPixmap = self.imageCache.createPixmap(
                self.editor.noChoiceIconPath)
            combobox.addItem(imgPixmap, noChoiceText, userData=noChoiceMethod)
            itemCounter = 1

        # Add items to add given types of objects
        if (addChoices):
            imgPixmap = self.imageCache.createPixmap(self.editor.newIconPath)
            for choice in addChoices:
                combobox.addItem(
                    imgPixmap, localizer.translate(
                        'classSettingsWidget', 'addNewChoice'),
                    userData=choice)
                itemCounter += 1

        for objType in objectTypes:
            objRooms = self.editor.getObjectsByType(objType)

            # Combobox has rooms with their obstacles under them
            for room in objRooms:
                roomObject = room["room"]
                roomName = roomObject.getName()
                if not (roomName):
                    roomName = localizer.translate(
                        'classSettingsWidget', 'roomHasNoName')
                imgPixmap = self.imageCache.createPixmap(
                    roomObject.getRepresentingImage().getRepresentingImage()
                    .absoluteImagePath)

                roomIcon = QtGui.QIcon(imgPixmap)

                # Add room to the combobox and disallow choosing it
                combobox.addItem(roomIcon, roomName)
                combobox.setItemData(itemCounter, 0, QtCore.Qt.UserRole - 1)
                itemCounter += 1

                # TODO: Indendation of objects in the combobox
                # Add objects under the room
                for obj in room["objects"]:
                    # Don't display the triggering item itself
                    if (obj == self.currentObject):
                        continue
                    if (obj.getClassname() == "Text"):
                        continue

                    imageObject = obj.getRepresentingImage()\
                        .getRepresentingImage()
                    imgPixmap = self.imageCache.createPixmap(
                        imageObject.absoluteImagePath)
                    targetIcon = QtGui.QIcon(imgPixmap)

                    objectName = obj.getName()
                    if not (objectName):
                        objectName = localizer.translate(
                            'classSettingsWidget', 'objectHasNoName')
                    combobox.addItem(targetIcon, objectName, userData=obj)
                    itemCounter += 1

    def showMusicDialog(self, callBack):
        if DEBUG:
            print("   [D] " + "SettingsWidget :: At showMusicDialog")
        fname, _ = QtGui.QFileDialog.getOpenFileName(
            self,
            localizer.translate(
                'classSettingsWidget', 'showMusicDialogChoose'),
            '~', localizer.translate(
                'classSettingsWidget', 'showMusicDialogFiles')
            )

        if (len(fname) != 0):
            self.musicTextEdit.setText(fname.split("/")[-1])
            callBack(fname)

    def showImageDialog(self, callBack):
        if DEBUG:
            print("   [D] " + "SettingsWidget :: At showImageDialog")
        fname, _ = QtGui.QFileDialog.getOpenFileName(
            self,
            localizer.translate(
                'classSettingsWidget', 'chooseBackground'),
            '~', localizer.translate(
                'classSettingsWidget', 'chooseBackgroundFiles')
            )

        if (len(fname) != 0):
            callBack(fname)

    def createSeparator(self):
        if DEBUG:
            print("   [D] " + "SettingsWidget :: At createSeparator")
        label = QtGui.QLabel("")
        label.setFrameStyle(QtGui.QFrame.HLine | QtGui.QFrame.Raised)
        return label
