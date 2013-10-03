import string, time
from api.plugin import Plugin, Result, Priority

class Tell(Plugin):

	def _start_(self):
		self.register_event('channel_message', Tell.on_msg, Priority.HIGH)
		self.register_event('join', Tell.on_join, Priority.HIGH)
		
	def _install_(self):
		self.sql.execute('CREATE TABLE `tell_tells` (target, time, sender, message)')
	
	def on_msg(self, data):
		print 'GETTING CALLED WITH %s' % data
		tells = self.sql.execute('SELECT * FROM `tell_tells` WHERE target = ? ORDER BY time ASC', (data['sender'],)).fetchall()
		for tell in tells:
			self.api.msg(data['channel'], ('[%s] %s: <%s> %s') % ( \
			self.time2str(time.time()-tell[1]),
			data['sender'],
			tell[2],
			tell[3]
			))
		if len(tells) != 0:
			self.sql.execute('DELETE FROM `tell_tells` WHERE target = ?', (data['sender'],))
			return
		
		message = string.split(data['message'])
		if len(message) >= 3 and message[0] == '.tell':
			#3 tell limit per person
			result = self.sql.execute('SELECT count(*) FROM `tell_tells` WHERE target = ? GROUP BY target', (message[1],)).fetchone()
			if result is not None and result[0] >= 3:
				self.api.msg(data['channel'], '%s: There are already 3 tells stored for that nickname' % data['sender'])
				return Result.PREVENT_ALL
			
			self.api.msg(data['channel'], '%s: gotcha' % data['sender'])
			target = message[1]
			msg = ' '.join(message[2:])
			self.sql.execute('INSERT INTO `tell_tells` VALUES (?,?,?,?)', (message[1], long(time.time()), data['sender'], msg))
		
			return Result.PREVENT_ALL
			
		return Result.SUCCESS
	
	def on_join(self, data):
		print 'JOIN GETTING CALLED WITH %s' % data
		tells = self.sql.execute('SELECT * FROM `tell_tells` WHERE target = ? ORDER BY time ASC', (data['sender'],)).fetchall()
		for tell in tells:
			self.api.msg(data['channel'], ('[%s] %s: <%s> %s') % ( \
			self.time2str(time.time()-tell[1]),
			data['sender'],
			tell[2],
			tell[3]
			))
		if len(tells) != 0:
			self.sql.execute('DELETE FROM `tell_tells` WHERE target = ?', (data['sender'],))

	def time2str(self, seconds):
		seconds = long(seconds)
		if(seconds >= 60*60*24):
			days = int(seconds / (60*60*24))
			if(days == 1): return '%d day ago' % days
			return '%d days ago' % days
		elif(seconds >= 60*60):
			hours = int(seconds / (60*60))
			if(hours == 1): return '%d hour ago' % hours
			return '%d hours ago' % hours
		elif(seconds >= 60):
			minutes = int(seconds / (60))
			if(minutes == 1): return '%d minute ago' % minutes
			return '%d minutes ago' % minutes
		else:
			if(seconds == 1): return '%d second ago' % seconds
			return '%d seconds ago' % seconds