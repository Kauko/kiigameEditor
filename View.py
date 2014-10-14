import Object
from random import randint


# Virtual class for views
class View(object):
    # Static method to create unique view ID
    usedIds = []

    def createUniqueId(newId=None):
        if not (newId):
            newId = str(randint(0, 1000000000))

        failed = False
        failCount = 0
        originalId = newId

        # Loop till unique ID found
        while (True):
            if not (newId in View.usedIds):
                if (failed):
                    print(
                        "Warning: Duplicate view ID '%s', new ID set as '%s'"
                        % (originalId, newId))
                View.usedIds.append(newId)
                return newId
            failCount += 1
            failed = True
            newId = "%s_duplicate_%i" % (originalId, failCount)

    def __init__(self, scenarioData, viewAttributes, viewId=None):
        if (viewId):
            self.id = View.createUniqueId(viewId)
        else:
            self.id = View.createUniqueId()

        self.scenarioData = scenarioData
        self.attrs = viewAttributes["attrs"]
        self.object = viewAttributes["object"]
        self.classname = viewAttributes["className"]

        if (self.id in scenarioData.texts):
            self.texts = scenarioData.texts[self.id]
        else:
            self.texts = {}

        self.placeholderImage = None  # If no representingImage, use this

        self.nameable = True

    # Should be overriden by other view classes
    def getChildren(self):
        return

    # Should be overriden by other view classes
    def getItems(self):
        return

    # Should be overriden by other view classes
    def getItemById(self, itemId):
        return

    def getName(self):
        try:
            return self.texts["name"]
        except:
            return None

    def setName(self, name):
        self.texts["name"] = name

    def getMusic(self):
        try:
            return self.object["music"]
        except KeyError:
            return

    def setMusic(self, filePath):
        self.object["music"] = "audio/"+filePath.split("/")[-1]

    def clearMusic(self):
        del self.object["music"]

    # Post-init should be overriden by views
    def postInit(self, getGameObject):
        return

    # Remove given object
    # Should be overriden by other view classes
    def removeObject(self, childObject):
        return

    def createPlaceholderImage(self, imagePath):
        self.placeholderImage = Object.JSONImage(self, None, None, self.id)
        self.placeholderImage.setSource(imagePath)


class Menu(View):
    def __init__(self, scenarioData, menuId, menuAttributes, menuImages):
        super(Menu, self).__init__(scenarioData, menuAttributes, menuId)

        self.menuImages = []
        for imageId in menuImages:
            image = menuImages[imageId].pop("image")[0]
            imageAttributes = menuImages[imageId]
            menuImage = Object.MenuImage(self, image, imageAttributes)
            self.menuImages.append(menuImage)

    def getItemById(self, itemId):
        for item in self.menuImages:
            if (item.id == itemId):
                return item

    def getChildren(self):
        return self.menuImages


# Game cutscenes
class Sequence(View):
    # Generic attributes for sequences
    sequenceAttributes = {
        'attrs': {
            'id': '',
            'object_name': '',
            'visible': False,
            'category': 'sequence'
        },
        'object': {
            'music': '',
            'images': {},
            'category': 'sequence'
        },
        'className': 'Layer'
    }

    generalName = "Välianimaatio"
    generalNameAdessive = "Välianimaatiolla"

    def __init__(self, scenarioData, sequenceId,
                 sequenceAttributes, sequenceImages):
        if not (sequenceAttributes):
            sequenceAttributes = Sequence.sequenceAttributes

        super(Sequence, self).\
            __init__(scenarioData, sequenceAttributes, sequenceId)

        self.sequenceImages = []

        if not (sequenceImages):
            return

        # Create sequence image objects
        for image in sequenceImages:
            images = sequenceImages[image].pop("image")[0]
            imageAttributes = sequenceImages[image]
            sequenceImage = Object.SequenceImage(self, images, imageAttributes)
            self.sequenceImages.append(sequenceImage)

    def deleteChild(self, imageId):
        for image in self.images:
            if (image.id == imageId):
                self.images.remove(image)

    def getChildren(self):
        return self.sequenceImages

    def getRepresentingImage(self):
        if (len(self.sequenceImages) == 0):
            return self.placeholderImage
        return self.sequenceImages[0]

    def getItems(self):
        return self.getChildren()

    # Get the display time for the given image
    def getShowTime(self, imageId):
        for i in self.object["images"]:
            if (self.object["images"][i]["id"] == imageId):
                return self.object["images"][i]["show_time"]

    # Set the display time for the given image
    def setShowTime(self, imageId, milliseconds):
        for i in self.object["images"]:
            if (self.object["images"][i]["id"] == imageId):
                self.object["images"][i]["show_time"] = milliseconds

    # Get the fade type for the given image
    def getDoFade(self, imageId):
        for i in self.object["images"]:
            if (self.object["images"][i]["id"] == imageId):
                return self.object["images"][i]["do_fade"]

    # Set the fade type for the given image
    def setDoFade(self, imageId, doFade):
        for i in self.object["images"]:
            if (self.object["images"][i]["id"] == imageId):
                self.object["images"][i]["do_fade"] = doFade

    # Create new item
    def addImage(self, objectAttributes=None, imageAttributes=None):
        imageId = self.id + "_image"
        newObject = Object.SequenceImage(
            self, objectAttributes, imageAttributes, imageId)
        self.sequenceImages.append(newObject)

        self.createImageEntry(newObject.id)

        return newObject

    # Create a new image entry to object
    def createImageEntry(self, imageId):
        images = self.object["images"]
        images[str(len(images) + 1)] = {
            'show_time': 0,
            'do_fade': False,
            'id': imageId
        }

    # Remove an image entry from objects
    def removeImageEntry(self, index):
        images = self.object["images"]
        del images[str(index)]

        # Move index of other images one index backwards
        for i in range(index+1, len(images)+2):
            entry = images.pop(str(i))
            images[str(i-1)] = entry

    # Remove a image from the sequence
    def removeObject(self, item):
        images = self.object["images"]

        # Remove from the entry
        for i in images:
            if (images[i]["id"] == item.id):
                self.removeImageEntry(int(i))
                break

        # Remove from actualy sequence images list
        self.sequenceImages.remove(item)

        # TODO: childObject not defined
        #self.scenarioData.removeObject(childObject)


# Start menu
class Start(View):
    generalName = "Alkukuva"
    generalNameAdessive = "Alkukuvalla"

    def __init__(self, scenarioData, startAttributes, startImages):
        super(Start, self).__init__(scenarioData, startAttributes, "start")

        self.nameable = False

        for imageId in startImages:
            imageAttributes = startImages[imageId].pop("image")[0]
            objectAttributes = startImages[imageId]
            imageId = imageAttributes["id"]

            # Create objects according to its category
            if (imageId == "begining"):
                self.beginingImage = Object.BeginingImage(
                    self, imageAttributes, objectAttributes)
            if (imageId == "start"):
                self.background = Object.JSONImage(
                    self, imageAttributes, objectAttributes)

    def postInit(self, getGameObject):
        # Create menu items
        menu = getGameObject("menu", self.object["menu"])
        try:
            for imageId, action in menu.object["items"].items():
                print("post", menu.object["items"].items())
                if (action == "start_game"):
                    self.startButton = menu.getItemById(imageId)
                elif (action == "credits"):
                    self.creditsButton = menu.getItemById(imageId)
                elif (action == "none"):
                    self.emptyButton = menu.getItemById(imageId)
        except AttributeError as e:
            print("View.Start :: WARNING, postInit(), NoneType-error")
            print("        "+str(e))

    def getChildren(self):
        ret = []

        # Put all of these in try-excepts because some attributes
        # were missing
        try:
            ret.append(self.background)
        except AttributeError as e:
            print("View.Start :: WARNING, " + str(e))
        try:
            ret.append(self.startButton)
        except AttributeError as e:
            print("View.Start :: WARNING, " + str(e))
        try:
            ret.append(self.creditsButton)
        except AttributeError as e:
            print("View.Start :: WARNING, " + str(e))
        try:
            ret.append(self.emptyButton)
        except AttributeError as e:
            print("View.Start :: WARNING, " + str(e))
        try:
            ret.append(self.beginingImage)
        except AttributeError as e:
            print("View.Start :: WARNING, " + str(e))

        return ret

    def getRepresentingImage(self):
        return self.background

    def getItems(self):
        return self.getChildren()


# End menu
class End(View):
    # Generic attributes for ends
    endAttributes = {
        'object': {
            'music': '',
            'sequence': '',
            'category': 'end',
            'menu': ''
        },
        'className': 'Layer',
        'attrs': {
            'category': 'end',
            'id': '',
            'visible': False,
            'object_name': ''
        }
    }

    generalName = "Pelin loppukuva"
    generalNameAdessive = "Loppukuvalla"

    def __init__(self, scenarioData, endId, endAttributes, endImages):
        if not (endAttributes):
            endAttributes = End.endAttributes

        super(End, self).__init__(scenarioData, endAttributes, endId)

        self.endImages = []
        self.endText = None

        self.nameable = False

        if not (endImages):
            return

        for imageId in endImages:
            imageAttributes = endImages[imageId].pop("image")[0]
            objectAttributes = endImages[imageId]
            imageId = imageAttributes["id"]

            self.endImages.append(
                Object.JSONImage(
                    self, imageAttributes, objectAttributes))

    def postInit(self, getGameObject):
        # Create text item
        # TODO: Connect texts and ends in kiigame to get rid of hard coded ID
        try:
            self.endText = getGameObject(
                "custom", "end_texts").getRepresentingImage()
        except AttributeError as e:
            print("View.End :: WARNING, postInit(), NoneType-error")
            print("        "+str(e))

    def deleteChild(self, imageId):
        for image in self.endImages:
            if (image.id == imageId):
                self.endImages.remove(image)

    def getChildren(self):
        return self.endImages

    def getItems(self):
        if (self.endText):
            return self.endText,
        return ()

    def getRepresentingImage(self):
        if (len(self.endImages) == 0):
            return self.placeholderImage
        return self.endImages[0]


# Any game room
class Room(View):
    # Generic attributes for rooms
    roomAttributes = {
        'className': 'Layer',
        'attrs': {
            'object_name': '',
            'id': '',
            'visible': False,
            'category': 'room',
            'start': False
        },
        'object': {
            'music': ''
        }
    }

    generalName = "Huone"
    generalNameAdessive = "Huoneella"

    def __init__(self, scenarioData, roomId, roomAttributes, roomImages):
        if not (roomAttributes):
            roomAttributes = Room.roomAttributes

        super(Room, self).__init__(scenarioData, roomAttributes, roomId)

        self.objectList = []
        self.background = None

        if not (roomImages):
            return

        # Create objects inside the room including the background
        # TODO: Parsing objects could as well be done in View?
        self.background = None
        for imageId in roomImages:
            images = roomImages[imageId].pop("image")
            imageAttributes = roomImages[imageId]
            imageCategory = images[0]["category"]

            # Create objects according to their category
            if (imageAttributes["className"] == "Text"):
                self.objectList.append(
                    Object.Text(self, images[0], imageAttributes, imageId))
            elif (imageCategory == "room_background"):
                self.background = Object.JSONImage(
                    self, images[0], imageAttributes)
            # TODO: Secret items - fix it in kiigame first
            elif (imageCategory == "item"):
                self.objectList.append(
                    Object.Item(self, imageId, images, imageAttributes))
            elif (imageCategory == "container"):
                self.objectList.append(
                    Object.Container(self, imageId, images, imageAttributes))
            elif (imageCategory == "door"):
                self.objectList.append(
                    Object.Door(self, imageId, images, imageAttributes))
            elif (imageCategory == "obstacle"):
                self.objectList.append(
                    Object.Obstacle(self, imageId, images, imageAttributes))
            else:
                self.objectList.append(
                    Object.Object(self, imageId, images, imageAttributes))

    def deleteChild(self, objectId):
        for obj in self.objectList:
            if (obj.id == objectId):
                self.objectList.remove(obj)

    def getChildren(self):
        return [self.background] + self.objectList

    def getItems(self):
        return self.objectList

    def getRepresentingImage(self):
        if (self.background):
            return self.background
        return self.placeholderImage

    def postInit(self, getGameObject):
        for obj in self.objectList:
            obj.postInit(getGameObject)

    # Create new generic object
    def addObject(self, objectAttributes=None, imageAttributes=None):
        imageId = self.id + "_object"
        newObject = Object.Object(
            self, imageId, imageAttributes, objectAttributes)
        self.objectList.append(newObject)
        return newObject

    # Create new item
    def addItem(self, objectAttributes=None, imageAttributes=None):
        imageId = self.id + "_item"
        newObject = Object.Item(
            self, imageId, imageAttributes, objectAttributes)
        self.objectList.append(newObject)
        return newObject

    # Move an existing item here
    def moveItem(self, item):
        self.objectList.append(item)

    # Create new container
    def addContainer(self, objectAttributes=None, imageAttributes=None):
        imageId = self.id + "_container"
        newObject = Object.Container(
            self, imageId, imageAttributes, objectAttributes)
        self.objectList.append(newObject)
        return newObject

    # Create new door
    def addDoor(self, objectAttributes=None, imageAttributes=None):
        imageId = self.id + "_door"
        newObject = Object.Door(
            self, imageId, imageAttributes, objectAttributes)
        self.objectList.append(newObject)
        return newObject

    # Create new obstacle
    def addObstacle(self, objectAttributes=None, imageAttributes=None):
        imageId = self.id + "_container"
        newObject = Object.Obstacle(
            self, imageId, imageAttributes, objectAttributes)
        self.objectList.append(newObject)
        return newObject

    def removeObject(self, childObject):
        self.objectList.remove(childObject)
        self.scenarioData.removeObject(childObject)

    def setItems(self, items):
        self.objectList = items


# Custom view for custom layers
class Custom(View):
    generalName = "Erikoisnäkymä"
    generalNameAdessive = "Erikoisnäkymällä"

    def __init__(self, scenarioData, viewId, viewAttributes, viewImages):
        super(Custom, self).__init__(scenarioData, viewAttributes, viewId)

        self.objectList = []
        for imageId in viewImages:
            images = viewImages[imageId].pop("image")
            imageAttributes = viewImages[imageId]

            if (imageAttributes["className"] == "Text"):
                newObject = Object.Text(
                    self, images[0], imageAttributes, imageId)
            else:
                newObject = Object.Object(
                    self, imageId, images, imageAttributes)
            self.objectList.append(newObject)

    def deleteChild(self, objectId):
        for obj in self.objectList:
            if (obj.id == objectId):
                self.objectList.remove(obj)

    def getChildren(self):
        return self.objectList

    def getRepresentingImage(self):
        return self.objectList[0]  # .getRepresentingImage()

    def getItems(self):
        return self.objectList
