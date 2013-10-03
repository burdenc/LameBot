class Priority():
	MAX = 5
	HIGH = 4
	NORMAL = 3
	LOW = 2
	LOG = 1
	
class Result():
	PREVENT_ALL = 1
	SUCCESS = None

#Abstract class, do not instantiate
class Plugin():
	def __init__(self, scheduler, bot, sql):
		self.api = bot
		self.sql = sql
		self._scheduler = scheduler
		
	def register_event(self, event_name, func, priority = Priority.NORMAL):
		self._scheduler.register_event(event_name, self, func, priority)
		
	def _install_(self):
		pass