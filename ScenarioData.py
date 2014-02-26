# -*- coding: cp1252 -*-

import json
import View, Object

class ScenarioData(object):
	def __init__(self):
		self.roomList = []
		self.objectList = []
		self.sequenceList = []
		self.characterImages = []
		self.menuView = None
		self.endView = None
		self.dataDir = "gamedata"

	# Load and parse game data files
	def loadScenario(self):
		# Load game data from files
		with open(self.dataDir + "/objects.json", encoding='utf-8') as f:
			objects = json.load(f)
			f.close()
			
		with open(self.dataDir + "/images.json", encoding="utf-8") as f:
			images = json.load(f)
			f.close()
			
		with open(self.dataDir + "/texts.json", encoding='utf-8') as f:
			texts = json.load(f)
			f.close()
			
		for child in images["children"]:
			#print (child)
			id = child["attrs"]["id"]
			category = child["attrs"]["category"]
			
			if (id == "start_layer"):
				self.menuView = View.Menu("start_layer")
				self.menuView.name = "Alkuvalikko"
				
				for image in child["children"]:
					image_id = image["attrs"]["id"]
					
					if (image_id == "start"):
						self.menuView.background = Object.JSONObject(image["attrs"])
						
					elif (image_id == "begining"):
						self.menuView.startImage = Object.JSONObject(image["attrs"])
						
					elif (image_id == "start_game"):
						startButton = Object.Object("start_game")
						startButton.name = "Aloituspainike"
						startButton.image = Object.JSONObject(image["attrs"])
						self.menuView.startButton = startButton
						
					elif (image_id == "start_credits"):
						creditsButton = Object.Object("start_credits")
						creditsButton.name = "Tekijät-painike"
						creditsButton.image = Object.JSONObject(image["attrs"])
						self.menuView.creditsButton = creditsButton
						
					elif (image_id == "start_empty"):
						emptyButton = Object.Object("start_empty")
						emptyButton.name = "Tyhjä painike"
						emptyButton.image = Object.JSONObject(image["attrs"])
						self.menuView.creditsButton = creditsButton
						
			elif (id == "end_layer"):
				endView = View.End("end_layer")
				endView.name = "Loppukuva"
				
				for image in child["children"]:
					image_id = image["attrs"]["id"]
					
					if (image_id.find("end_picture_") != -1):
						picture = Object.JSONObject(image["attrs"])
						endView.endPictures.append(picture)
						
					elif (image_id == "rewards_text"):
						endView.endText = Object.JSONObject(image["attrs"], "Text")
				self.endView = endView
				
			elif (id == "background_layer"):
				pass
				
			# TODO: Character layer
			elif (id == "character_layer"):
				print("char")
						
			elif (category == "sequence"):
				sequence = View.Sequence(child["attrs"]["id"])
				
				for image in child["children"]:
					image =  Object.JSONObject(image["attrs"])
					sequence.images.append(image)
					
				self.sequenceList.append(sequence)
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
