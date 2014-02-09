import string, time
from api.plugin import Plugin, Result, Priority

class Tell(Plugin):

	def _start_(self):
		self.logger.info('Starting Tell plugin')
		self.register_event('channel_message', Tell.on_msg, Priority.HIGH)
		self.register_event('join', Tell.on_join, Priority.HIGH)
		
	def _install_(self):
		self.sql.execute('CREATE TABLE `tell_tells` (target, time, sender, message, network)')
	
	def on_msg(self, data, network):
		self.logger.debug('on_msg called with %s', data)
		tells = self.sql.execute('SELECT * FROM `tell_tells` WHERE target = ? AND network = ? ORDER BY time ASC', (data['sender'], network.name)).fetchall()
		for tell in tells:
			network.msg(data['channel'], ('[%s] %s: <%s> %s') % ( \
			self.time2str(time.time()-tell[1]),
			data['sender'],
			tell[2],
			tell[3]
			))
		if len(tells) != 0:
			self.sql.execute('DELETE FROM `tell_tells` WHERE target = ? AND network = ?', (data['sender'], network.name))
		
		
		message = string.split(data['message'])
		if len(message) >= 3 and message[0] == '.tell':
			#3 tell limit per person
			result = self.sql.execute('SELECT count(*) FROM `tell_tells` WHERE target = ? AND network = ? GROUP BY target', (message[1], network.name)).fetchone()
			if result is not None and result[0] >= 3:
				network.msg(data['channel'], '%s: There are already 3 tells stored for that nickname' % data['sender'])
				return Result.PREVENT_ALL
			
			network.msg(data['channel'], '%s: gotcha' % data['sender'])
			target = message[1]
			msg = ' '.join(message[2:])
			self.sql.execute('INSERT INTO `tell_tells` VALUES (?,?,?,?,?)', (message[1], long(time.time()), data['sender'], msg, network.name))
		
			return Result.PREVENT_ALL
			
		return Result.SUCCESS
	
	def on_join(self, data, network):
		self.logger.debug('on_join called with %s', data)
		tells = self.sql.execute('SELECT * FROM `tell_tells` WHERE target = ? AND network = ? ORDER BY time ASC', (data['sender'], network.name)).fetchall()
		for tell in tells:
			network.msg(data['channel'], ('[%s] %s: <%s> %s') % ( \
			self.time2str(time.time()-tell[1]),
			data['sender'],
			tell[2],
			tell[3]
			))
		if len(tells) != 0:
			self.sql.execute('DELETE FROM `tell_tells` WHERE target = ? AND network = ?', (data['sender'], network.name))

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