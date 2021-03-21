from getopt import getopt, GetoptError
import sys


class Config(object):
    channels_uri_path = b"/channels"
    clients_uri_path = b"/clients"
    status_uri_path = b"/status"
    channels_sep = "|"
    default_format = b"json"
    jsonp_required_substr = "_JSONP_"
    default_jsonp_cb = jsonp_required_substr + "comet_cb"
    http_cache_age = 1
    default_max_messages_per_channel = 100

    def __init__(self, args):
        self._http_port = None
        self._http_timeout = 30
        self._unix_socket_path = None
        self._client_session_timeout = 60
        self._inactive_channel_timeout = 90
        self._max_messages_per_second = 100000
        self._quote_json = False
        self._enable_status = False
        opts = [
            "http-port=",
            "http-timeout=",
            "unix-socket-path=",
            "session-timeout=",
            "inactive-channel-timeout=",
            "max-messages-per-channel=",
            "quote-json",
            "enable-status",
        ]
        try:
            optlist, args = getopt(args, list(), opts)
        except GetoptError:
            self.help()

        for opt in optlist:
            self.parse_opt(opt)

    def help(self):
        print(
            """
Usage: simple_comet
            
--http-port=<HTTP server port> (default=none)
--unix-socket-path=<path to UNIX socket> (default=none)
--http-timeout=<HTTP timeout in seconds> (default=30)
--session-timeout=<session timeout in seconds> (default=60)
--inactive-channel-timeout=<inactive channel timeout> (default=90)
--messages-per-channel=<default max messages per channel> (default=100)
--quote-json
--enable-status
"""
        )
        sys.exit(0)

    def parse_opt(self, opt):
        switch, arg = opt
        if switch == "--http-port":
            self.http_port = int(arg)
        elif switch == "--http-timeout":
            self.http_timeout = int(arg)
        elif switch == "--unix-socket-path":
            self.unix_socket_path = arg
        elif switch == "--session-timeout":
            self.client_session_timeout = int(arg)
        elif switch == "--inactive-channel-timeout":
            self.inactive_channel_timeout = int(arg)
        elif switch == "--max-messages_per_channel":
            self.default_max_messages_per_channel = int(arg)
        elif switch == "--quote-json":
            self.quote_json = True
        elif switch == "--enable-status":
            self.enable_status = True
        else:
            assert False

    def set_http_port(self, value):
        assert value in range(0, 65536)
        self._http_port = value

    http_port = property(lambda self: self._http_port, set_http_port)

    def set_http_timeout(self, value):
        assert value > 0
        self._http_timeout = value

    http_timeout = property(lambda self: self._http_timeout, set_http_timeout)

    def set_unix_socket_path(self, value):
        assert value
        self._unix_socket_path = value

    unix_socket_path = property(
        lambda self: self._unix_socket_path, set_unix_socket_path
    )

    def set_client_session_timeout(self, value):
        assert value > 0
        self._client_session_timeout = value

    client_session_timeout = property(
        lambda self: self._client_session_timeout, set_client_session_timeout
    )

    def set_inactive_channel_timeout(self, value):
        assert value > 0
        self._inactive_channel_timeout = value

    inactive_channel_timeout = property(
        lambda self: self._inactive_channel_timeout, set_inactive_channel_timeout
    )

    def set_max_messages_per_second(self, value):
        assert value > 0
        self._max_messages_per_second = value

    max_messages_per_second = property(
        lambda self: self._max_messages_per_second, set_max_messages_per_second
    )

    def set_quote_json(self, value):
        self._quote_json = value

    quote_json = property(lambda self: self._quote_json, set_quote_json)

    def set_enable_status(self, value):
        self._enable_status = value

    enable_status = property(lambda self: self._enable_status, set_enable_status)
