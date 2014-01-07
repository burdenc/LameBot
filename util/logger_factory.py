import logging, util.logger_factory

_instance = None

def instance():
	return _instance

class LoggerFactory():

	def __init__(self):
		self.handlers = []
		self.formatter = None
		util.logger_factory._instance = self

	def addHandler(self, handler):
		self.handlers.append(handler)
	
	def setFormatter(self, formatter):
		self.formatter = formatter
		
	def setMinLevel(self, min_level):
		self.min_level = min_level
	
	def getLogger(self, name):
		logger = logging.getLogger(name)
		for handler in self.handlers: handler.setFormatter(self.formatter)
		for handler in self.handlers: logger.addHandler(handler)
		logger.setLevel(self.min_level)
		return logger
	