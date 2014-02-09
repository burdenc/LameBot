#TODO: flesh out irc.py api
#TODO: add functionality to control bot via DCC or private message (PRIVMSG ^ACTCP DCC CHAT <host> <port>^A)
#TODO: convert all channels to lowercase (because IRC network will do that)
#TODO: add _uninstall_() function for plugins

import net.irc, net.response, net.dcc, api.scheduler, api.loader, util.logger_factory, util.config
import sys, time, sqlite3, select, string

class Bot():
	def __init__(self, conf_file):
		config = util.config.parse_config(conf_file)
		self.logger = util.logger_factory.instance().getLogger('main')
		
		network_configs = config['nets']
		self.network_list = []

		self.sql_conn = sqlite3.connect('bot.db')
		self.logger.debug('sqlite connection created')

		#Instantiate each network connection based on config file
		for network in network_configs:
			connection = net.irc.IRC(
				network['_name_'],
				network['address'],
				int(network['port']),
				network['nick'],
				network['real_name'],
				network['channels'],
				network['extensions'],
				network['allowed_channels']
			)
			connection.connect()
			self.network_list.append(connection)
			

		self.scheduler = api.scheduler.Scheduler()
		loader = api.loader.Loader(self.scheduler, self, self.sql_conn)
		loader.load_all(config['extensions'])


	def run(self):
		responder = net.response.Response()
		while True:
			#Wait for sockets to raise flag saying bytes are available to be read
			connections = select.select(self.network_list, [], [])[0]
			for connection in connections:
				
				if isinstance(connection, net.dcc.DCCPassive):
					client_socket = connection.accept()
					
					#Convert Passive DCC socket to regular one now 
					#that incoming connection is accepted
					dcc_conn = net.dcc.DCC(socket = client_socket)
					
					self.network_list.remove(connection)
					client_socket.sendall('Test!\r\n')
					continue
				
				for line in connection.poll():
					line = string.rstrip(line)
					#not whitespace
					if line:
						response = responder.parse(line)
						if response['type'] != 'unknown':
							if response['data']: data = response['data']
							else: data = None
							self.scheduler.call_event(response['type'], data, connection)
							self.sql_conn.commit()
						if response['type'] == 'connect':
							connection.join()
						if response['type'] == 'ping':
							connection._send_raw(net.irc.Commands.PONG(response['data']['sender']))
						if response['type'] == 'dcc_chat':
							self.logger.info('DCC request received from: %s:%s', response['data']['dcchost'], response['data']['dccport'])
							dcc_conn = net.dcc.DCC(response['data']['dcchost'], response['data']['dccport'])
							dcc_conn.connect()
							dcc_conn._send_raw('Test!')
						if response['type'] == 'passive_dcc_chat':
							self.logger.info('Passive DCC request received from %s', response['data']['sender'])
							dcc_conn = net.dcc.DCCPassive()
							dcc_conn.bind()
							host = net.dcc.ip_to_int(connection.get_ext_address()[0])
							connection.ctcp(response['data']['sender'], 'DCC CHAT chat %s %s' % (host, dcc_conn.port))
							self.network_list.append(dcc_conn)
	
if __name__ == '__main__':
	try:
		conf_file = sys.argv[1]
	except IndexError:
		conf_file = 'bot.conf'
	
	bot = Bot(conf_file)
	bot.run()