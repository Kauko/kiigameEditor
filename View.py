import Object
from random import randint

# Virtual class for views
class View(object):
	def __init__(self, id=None):
		# TODO: Check id collision, "running" id instead randint?
		#		Static ID counter?
		if not (id):
			self.id = int(randint(0, 1000000000))
		self.name = ""
		self.music = ""
		self.type = ""

# Game cutscenes
class Sequence(View):
	def __init__(self, id=None):
		super(Sequence, self).__init__(id)
		self.images = []

# Start menu
class Menu(View):
	def __init__(self, id=None):
		super(Menu, self).__init__(id)
		self.background = None
		self.startButton = None
		self.creditsButton = None
		self.emptyButton = None
		self.startImage = None

# End menu
class End(View):
	def __init__(self, id=None):
		super(End, self).__init__(id)
		# TODO: End pictures are stupid
		# TODO: Before handling that, arrange pictures for UI?
		self.endPictures = []
		self.endText = None
		
# Any game room
class Room(View):
	def __init__(self, id=None):
		super(Room, self).__init__(id)
		self.objectList = []
		self.background = None
		self.comingFrom = []
