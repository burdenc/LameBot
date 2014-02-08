#TODO: flesh out irc.py api
#TODO: add functionality to control bot via DCC or private message (PRIVMSG ^ACTCP DCC CHAT <host> <port>^A)
#TODO: convert all channels to lowercase (because IRC network will do that)
#TODO: add _uninstall_() function for plugins

import net.irc, net.response, net.dcc, net.dcc_passive, api.scheduler, api.loader, util.logger_factory, util.config
import sys, time, sqlite3, select, string

class Bot():
	def __init__(self, conf_file):
		config = util.config.parse_config(conf_file)
		self.logger = util.logger_factory.instance().getLogger('main')
		
		self.network_list = config['nets']

		self.conn = sqlite3.connect('bot.db')
		self.logger.debug('sqlite connection created')
		
		#Used to have non-blocking polling of each network via select.select()
		#Stores file descriptor of each socket object
		self.socket_fd_list = []

		for network in self.network_list:
			connection = net.irc.IRC(network['_name_'])
			connection.connect(
				network['address'],
				int(network['port']),
				network['nick'],
				network['real_name'],
				network['channels']
			)
			network['connection'] = connection
			self.socket_fd_list.append(connection)

		self.scheduler = api.scheduler.Scheduler()
		loader = api.loader.Loader(self.scheduler, self, self.conn)
		loader.load_all(config['extensions'])


	def run(self):
		responder = net.response.Response()
		while True:
			networks = select.select(self.socket_fd_list, [], [])[0]
			for network in filter(lambda x: x['connection'] in networks, self.network_list):
				#network = self.network_list[0]
				connection = network['connection']
				
				if isinstance(connection, net.dcc_passive.DCCPassive):
					client_socket = connection.accept()
					dcc_conn = net.dcc.DCC(client_socket)
					self.socket_fd_list.remove(connection)
					self.network_list.remove(network)
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
							self.scheduler.call_event(response['type'], data, network)
							self.conn.commit()
						if response['type'] == 'connect':
							connection.join()
						if response['type'] == 'ping':
							connection._send_raw(net.irc.Commands.PONG(response['data']['sender']))
						if response['type'] == 'dcc_chat':
							self.logger.info('DCC request received from: %s:%s', response['data']['dcc']['dcchost'], response['data']['dcc']['dccport'])
							dcc_conn = net.dcc.DCC(response['data']['dcc']['dcchost'], response['data']['dcc']['dccport'])
							dcc_conn.connect()
							dcc_conn._send_raw('Test!')
						if response['type'] == 'passive_dcc_chat':
							self.logger.info('Passive DCC request received from %s', response['data']['sender'])
							dcc_conn = net.dcc_passive.DCCPassive()
							dcc_conn.bind()
							host = net.dcc_passive.ip_to_int(connection.get_ext_address()[0])
							connection.ctcp(response['data']['sender'], 'DCC CHAT chat %s %s' % (host, dcc_conn.port))
							self.socket_fd_list.append(dcc_conn)
							self.network_list.append({'connection':dcc_conn})
	
if __name__ == '__main__':
	try:
		conf_file = sys.argv[1]
	except IndexError:
		conf_file = 'bot.conf'
	
	bot = Bot(conf_file)
	bot.run()