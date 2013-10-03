import socket, string, time, re

class IRC():

	def connect(self, host, port = 6667, nick = 'DBBot', real_name = 'My bot', channels = []):
		self.host = host
		self.port = port
		self.nick = nick
		self.real_name = real_name
		self.chan_list = channels
		channels = ','.join(channels)
		
		self._conn_socket = socket.socket()
		#No buffer
		self._conn_socket.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
		self._conn_socket.connect((host, port))
		
		self._send_raw(Commands.NICK(nick))
		self._send_raw(Commands.USER(nick, real_name))
		
	def disconnect(self, reason = 'cya nerds'):
		self._send_raw(Commands.QUIT(reason))
		self._conn_socket.close()
	
	#Channels is comma delimited str
	def join(self, channels = None):
		if channels is None:
			channels = self.chan_list
			channels = ','.join(channels)
		self._send_raw(Commands.JOIN(channels))
		
	def msg(self, target, message):
		self._send_raw(Commands.PRIVMSG(target, message))
		
	def poll(self):
		buffer = self._conn_socket.recv(1024)
		buffer = string.rstrip(buffer)
		buffer = string.split(buffer, '\r\n')
		return buffer
		
	def _send_raw(self, message):
		if message[-2:] != '\r\n':
			message += '\r\n'
		print 'SENDING: %s' % message[:-2]
		sent = self._conn_socket.sendall(message)

#Commonly received message syntax
class Response():
	possible_responses = {
		'connect' : re.compile(r'^(?P<sender>.+) 001 .*$'), #001 connection numeric
		'channel_message' : re.compile(r'^:(?P<sender>.+)!(?P<host>.+) PRIVMSG (?P<channel>#.+) :(?P<message>.*)$'),
		'join' : re.compile(r'^:(?P<sender>.+)!(?P<host>.+) JOIN :?(?P<channel>#.+)$'),
		'ping' : re.compile(r'^PING (?P<sender>.+)$')
	}
	
	@staticmethod
	def parse(message):
		print message
		message = string.split(message, ' ')
		parsed = {'type':'unknown'}
		
		for response, regex in Response.possible_responses.iteritems():
			match = regex.match(' '.join(message))
			if match:
				parsed['type'] = response
				parsed['data'] = match.groupdict()
				break
		
		return parsed
		
	
	#TODO: make pythonic
	@staticmethod
	def parse_hostname(hostname):
		dict = {}
		split = hostname.partition('!')[0]
		dict['nick'] = split[0]
		split = split[2].partition('@')
		dict['realname'] = split[0]
		dict['host'] = split[2]
		return dict
		
	
#Commonly called command syntax
class Commands():
	
	@staticmethod
	def PRIVMSG(target, message):
		return 'PRIVMSG %s :%s\r\n' % (target, message)
	
	@staticmethod
	def QUIT(message = 'Bye'):
		return 'QUIT %s\r\n' % (message)
	
	@staticmethod
	def JOIN(channels):
		return 'JOIN :%s\r\n' % (channels)
	
	@staticmethod
	def PONG(host):
		return 'PONG %s\r\n' % (host)
	
	@staticmethod
	def USER(nick, real_name):
		return 'USER %s * 8 :%s\r\n' % (nick, real_name)
	
	@staticmethod
	def NICK(nick):
		return 'NICK %s\r\n' % nick