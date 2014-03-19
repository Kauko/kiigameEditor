from PySide import QtGui, QtCore

# Singleton image cacher to prevent them being loaded more than once
class ImageCache(object):
	_instance = None
	def __new__(cls, *args, **kwargs):
		if not cls._instance:
			cls._instance = super(ImageCache, cls).__new__(cls, *args, **kwargs)
		return cls._instance
		
	def __init__(self):
		self.images = {}
		
	# Create image with given path if it doesn't exist,
	# otherwise return the already existing one
	def createPixmap(self, absolutePath):
		if (absolutePath in self.images):
			return self.images[absolutePath]
			
		imgPixmap = QtGui.QPixmap(absolutePath)
		self.images[absolutePath] = imgPixmap
		
		return imgPixmap
