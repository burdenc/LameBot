import ConfigParser, string, logging, collections
import util.logger_factory

def parse_config(conf_file):
		config = ConfigParser.ConfigParser()
		config.read([conf_file])
		
		defaults = {'min_log_level' : 'INFO', 'log_file_path' : 'bot.log', 'log2stdout' : True}
		config._defaults = collections.OrderedDict(defaults)
		
		load_extensions = []
		try:
			load_extensions = config.get('~~Bot~~', 'load_extensions')
			if load_extensions != '~~All~~':
				load_extensions = string.split(load_extensions, ',')
		except ConfigParser.NoOptionError:
			load_extensions = []
			
		stdout = config.getboolean('~~Bot~~', 'log2stdout')
		
		levels = ['INFO', 'DEBUG', 'CRITICAL', 'ERROR', 'WARNING']
		min_level = string.upper(config.get('~~Bot~~', 'min_log_level'))
		min_level = getattr(logging, min_level) if min_level in levels else logging.INFO
		logger = _config_logger(stdout, min_level, config.get('~~Bot~~', 'log_file_path'))
		
		#---Logging Enabled---
		#TODO: Create temporary list for any loggings raised before logs are configured
		#      This should be reserved for very critical errors
		
		if load_extensions == '~~All~~':
			logger.warning('load_extensions value set to load all extensions. Could be dangerous, please ensure all plugins in \'ext\' folder are not malicious.')
		
		config._defaults = collections.OrderedDict()
		defaults = config.items('~~Global~~')
		config._defaults = collections.OrderedDict(defaults)
		
		network_list = []
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
			network_list.append(items)
		
		return {'nets' : network_list, 'extensions' : load_extensions}

def _config_logger(stdout = True, min_level = logging.INFO, output_file = 'bot.log'):
	logger_factory = util.logger_factory.LoggerFactory()
	logger_factory.addHandler(logging.FileHandler(output_file))
	if stdout:
		logger_factory.addHandler(logging.StreamHandler())
		
	format = '[%(asctime)s] %(levelname)-8s %(name)s: %(message)s'
	dateformat = '%b %d, %Y %H:%M:%S'
	logger_factory.setFormatter(logging.Formatter(format, dateformat))
	
	logger_factory.setMinLevel(min_level)
	return util.logger_factory.instance().getLogger('util.config')