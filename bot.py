#TODO: flesh out irc.py api
#TODO: add functionality to control bot via DCC or private message (PRIVMSG ^ACTCP DCC CHAT <host> <port>^A)
#TODO: convert all channels to lowercase (because IRC network will do that)
#TODO: add _uninstall_() function for plugins

import net.irc, net.response, net.dcc, api.scheduler, api.loader, util.logger_factory
import sys, string, time, sqlite3, ConfigParser, collections, logging, select

class Bot():
	def __init__(self, conf_file):
		self._parse_config(conf_file)

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
		loader.load_all(self.load_extensions)


	def run(self):
		responder = net.response.Response()
		while True:
			networks = select.select(self.socket_fd_list, [], [])[0]
			for network in filter(lambda x: x['connection'] in networks, self.network_list):
				#network = self.network_list[0]
				connection = network['connection']
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
						#print response
						if response['type'] == 'connect':
							connection.join()
						if response['type'] == 'ping':
							connection._send_raw(net.irc.Commands.PONG(response['data']['sender']))
						if response['type'] == 'dcc_chat':
							self.logger.info('DCC request received from: %s:%s', response['data']['dcchost'], response['data']['dccport'])
							dcc_conn = net.dcc.DCC(response['data']['dcchost'], response['data']['dccport'])
							dcc_conn.connect()
							dcc_conn._send_raw('Test!')
					
	def _parse_config(self, conf_file):
		config = ConfigParser.ConfigParser()
		config.read([conf_file])
		
		defaults = {'min_log_level' : 'INFO', 'log_file_path' : 'bot.log', 'log2stdout' : True}
		config._defaults = collections.OrderedDict(defaults)
		
		try:
			self.load_extensions = config.get('~~Bot~~', 'load_extensions')
			if self.load_extensions != '~~All~~':
				self.load_extensions = string.split(self.load_extensions, ',')
		except ConfigParser.NoOptionError:
			self.load_extensions = []
			
		stdout = config.getboolean('~~Bot~~', 'log2stdout')
		
		levels = ['INFO', 'DEBUG', 'CRITICAL', 'ERROR', 'WARNING']
		min_level = string.upper(config.get('~~Bot~~', 'min_log_level'))
		min_level = getattr(logging, min_level) if min_level in levels else logging.INFO
		self._config_logger(stdout, min_level, config.get('~~Bot~~', 'log_file_path'))
		
		#---Logging Enabled---
		#TODO: Create temporary list for any loggings raised before logs are configured
		#      This should be reserved for very critical errors
		
		if self.load_extensions == '~~All~~':
			self.logger.warning('load_extensions value set to load all extensions. Could be dangerous, please ensure all plugins in \'ext\' folder are not malicious.')
		
		config._defaults = collections.OrderedDict()
		defaults = config.items('~~Global~~')
		config._defaults = collections.OrderedDict(defaults)
		
		self.network_list = []
		for section in config.sections():
			if section == '~~Global~~' or section == '~~Bot~~': continue
			items = config.items(section)
			items = dict(items)
			items['allowed_channels'] = {}
			
			channels = string.split(items['channels'], ';')
			items['channels'] = [string.split(x, ',')[0] for x in channels]
			for channel in channels:
				try:
					split_data = string.split(channel, ',')
					channel = split_data[0]
					extensions = split_data[1:]
				except KeyError:
					continue
				
				for extension in extensions:
					try:
						items['allowed_channels'][extension] += channel
					except KeyError:
						items['allowed_channels'][extension] = [channel]
			
			items['_name_'] = section
			self.network_list.append(items)
			
	def _config_logger(self, stdout = True, min_level = logging.INFO, output_file = 'bot.log'):
		logger_factory = util.logger_factory.LoggerFactory()
		logger_factory.addHandler(logging.FileHandler(output_file))
		if stdout:
			logger_factory.addHandler(logging.StreamHandler())
			
		format = '[%(asctime)s] %(levelname)-8s %(name)s: %(message)s'
		dateformat = '%b %d, %Y %H:%M:%S'
		logger_factory.setFormatter(logging.Formatter(format, dateformat))
		
		logger_factory.setMinLevel(min_level)
		self.logger = util.logger_factory.instance().getLogger('main')
		
		
	
if __name__ == '__main__':
	try:
		conf_file = sys.argv[1]
	except IndexError:
		conf_file = 'bot.conf'
	
	bot = Bot(conf_file)
	bot.run()