import re
from api.plugin import Plugin, Result, Priority

password = '12345678900abcdef'
	
possible_responses = {
	'message' : re.compile(r'^MESSAGE (?P<network>.+) (?P<channel>.+) (?P<message>.+)$')
}

class DCCControl(Plugin):

	def _start_(self):
		self.logger.info('Starting DCC Control plugin')
		self.register_event('dcc_connect', DCCControl.on_dcc_connect)
		self.register_event('dcc_message', DCCControl.on_dcc_msg)
		self.register_event('dcc_disconnect', DCCControl.on_dcc_disconnect)
		
		self.conn_ident_list = {}
		
	def _install_(self):
		pass
		
	def _uninstall_(self):
		pass
	
	def on_dcc_msg(self, data, conn):
		if self.conn_ident_list[conn] is False:
			if data['message'] == password:
				self.conn_ident_list[conn] = True
				conn.msg('Thank you for authenticating, you now have full access to this bot')
			else:
				conn.msg('Incorrect password.')
				conn.disconnect()
				del self.conn_ident_list[conn]
				self.api.remove(conn)
			return
		
		for response, regex in possible_responses.iteritems():
			match = regex.match(data['message'])
			if match:
				self.respond(response, match.groupdict())
		
	def on_dcc_connect(self, data, conn):
		self.conn_ident_list[conn] = False
		conn.msg('Please provide the bot password to authenticate yourself.')
		
	def on_dcc_disconnect(self, data, conn):
		del self.conn_ident_list[conn]
		
	def respond(self, type, data):
		if type == 'message':
			for network in self.api:
				if network.name != data['network']:
					continue
				
				network.msg(data['channel'], data['message'])
				break