import Object

# Virtual class for views
class View(object):
	def __init__(self):
		self.id = ""
		self.name = ""
		self.music = ""
		self.type = ""

# Game cutscenes
class Sequence(View):
	def __init__(self):
		super(Sequence, self).__init__()
		self.images = []

# Start menu
class Menu(View):
	def __init__(self):
		super(Menu, self).__init__()
		self.background = ""
		self.startButton = None
		self.creditsButton = None
		self.startImage = ""

# Any game room
class Room(View):
	def __init__(self):
		super(Room, self).__init__()
		self.objectList = []
		self.background = ""
		self.comingFrom = 
