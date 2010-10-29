
class Config(object):
	channels_uri_path = "/channels"
	handshake_uri_path = "/handshake"
	channels_sep = "|"
	default_format = "json"
	jsonp_required_substr = "_JSONP_"
	default_jsonp_cb = jsonp_required_substr + "comet_cb"	
	
	def __init__(self):
		self._http_port = 8080
		self._http_timeout = 30
		self._client_session_timeout = 60
		self._max_messages_per_second = 100000
		self._quote_jsonp = False

		
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

				
HTTP_CACHE_AGE = 86400 * 90
DEFAULT_MAX_MESSAGES_PER_CHANNEL = 5
