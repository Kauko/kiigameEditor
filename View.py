import Object
from random import randint

# Virtual class for views
class View(object):
	def __init__(self, name, id=None):
		# TODO: Check id collision, "running" id instead randint?
		#		Static ID counter?
		if not (id):
			self.id = int(randint(0, 1000000000))
		self.name = name
		self.music = ""
		self.type = ""

# Game cutscenes
class Sequence(View):
	def __init__(self):
		super(Sequence, self).__init__()
		self.images = []

# Start menu
class Menu(View):
	def __init__(self, name, id=None):
		super(Menu, self).__init__(name, id)
		self.background = ""
		self.startButton = None
		self.creditsButton = None
		self.startImage = ""
		
		#self.addOption()
		#self.addOption()
		
	def addOption(self):
		print ("opstiooni")

# Any game room
class Room(View):
	def __init__(self):
		super(Room, self).__init__()
		self.objectList = []
		self.background = ""
		self.comingFrom = ""
