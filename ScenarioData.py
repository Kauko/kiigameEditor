import json
import View

class ScenarioData(object):
	def __init__(self):
		self.roomList = []
		self.objectList = []
		self.sequenceList = []
		self.menuView = None
		self.dataDir = "gamedata"

	# Load and parse game data files
	def loadScenario(self):
		# Load game data from files
		with open(self.dataDir + "/objects.json") as f:
			objects = json.load(f)
			f.close()
			
		with open(self.dataDir + "/images.json") as f:
			images = json.load(f)
			f.close()
			
		with open(self.dataDir + "/texts.json") as f:
			texts = json.load(f)
			f.close()
			
		for child in images["children"]:
			#print(child["attrs"])
			id = child["attrs"]["id"]
			category = child["attrs"]["category"]
			
			if (id == "start_layer"):
				print ("start")
				view = View.Menu("Alkuvalikko")
				
				for image in child["children"]:
					print (image)
					image_id = image["attrs"]["id"]
					
					if (image_id == "start"):
						view.background = image["attrs"]["src"]
					if (image_id == "begining"):
						view.startImage = image["attrs"]["src"]
						
						
				print(view.startImage)
				
			elif (id == "end_layer"):
				#print ("end")
				pass
			elif (id == "background_layer"):
				#print ("bgs")
				pass
			elif (id == "character_layer"):
				print("char")
						
			elif (category == "sequence"):
				#print ("sequence")
				pass
		return

	def saveScenario(self):
		return

	def addView(self):
		return

	def addObject(self):
		return

	def deleteView(self):
		return

	def deleteObject(self):
		return

	def getObject(self):
		return

	def getView(self):
		return

	def editObject(self):
		return

	def editUse(self):
		return

sc = ScenarioData()
sc.loadScenario()