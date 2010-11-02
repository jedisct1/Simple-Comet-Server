
from getopt import getopt, GetoptError
import sys


class Config(object):
	channels_uri_path = "/channels"
	handshake_uri_path = "/handshake"
	clients_uri_path = "/clients"	
	channels_sep = "|"
	default_format = "json"
	jsonp_required_substr = "_JSONP_"
	default_jsonp_cb = jsonp_required_substr + "comet_cb"
	http_cache_age = 86400 * 90
	default_max_messages_per_channel = 10
	anonymous_client_id = "anonymous"
	
	
	def __init__(self, args):
		self._http_port = 8080
		self._http_timeout = 30
		self._client_session_timeout = 60
		self._max_messages_per_second = 100000
		self._quote_jsonp = False
		opts = [ "http-port=", "http-timeout=", "session-timeout=",
		         "max-messages-per-channel=", "quote-jsonp" ]
		try:
			optlist, args = getopt(args, None, opts)
		except GetoptError:
			self.help()
			
		for opt in optlist:
			self.parse_opt(opt)


	def help(self):
		print """
Usage: simple_comet
            
--http-port=<HTTP server port>
--http-timeout=<HTTP timeout in seconds>
--session-timeout=<session timeout in seconds>
--messages-per-channel=<default max messages per channel>
--quote-jsonp
"""
		sys.exit(0)
		

	def parse_opt(self, config, opt):
		switch, arg = opt
		if switch == "--http-port":
			config.http_port = int(arg)
		elif switch == "--http-timeout":
			config.http_timeout = int(arg)
		elif switch == "--session-timeout":
			config.session_timeout = int(arg)
		elif switch == "--max-messages_per_channel":
			config.max_messages_per_channel = int(arg)
		elif switch == "--quote-jsonp":
			config.quote_jsonp = True
		else:
			assert(False)			
			
							
	@property
	def http_port(self):
		return self._http_port

	
	@http_port.setter
	def http_port(self, value):
		assert(value in range(0, 65536))
		self._http_port = value


	@property
	def http_timeout(self):		
		return self._http_timeout

	
	@http_timeout.setter
	def http_timeout(self, value):
		assert(value > 0)
		self._http_timeout = value
		
		
	@property
	def client_session_timeout(self):
		return self._client_session_timeout

	
	@client_session_timeout.setter
	def client_session_timeout(self, value):
		assert(value > 0)
		self._client_session_timeout = value


	@property
	def max_messages_per_second(self):
		return self._max_messages_per_second

	
	@max_messages_per_second.setter
	def max_messages_per_second(self, value):
		assert(value > 0)
		self._max_messages_per_second = value


	@property
	def quote_jsonp(self):
		return self._quote_jsonp

	
	@quote_jsonp.setter
	def quote_jsonp(self, value):
		self._quote_jsonp = value

