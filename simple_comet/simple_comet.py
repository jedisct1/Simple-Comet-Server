
from config import *
from twisted.internet import reactor
from twisted.web import server, resource, http
from comet_server import CometServer
from getopt import getopt, GetoptError
import sys


def help():
    print """
Usage: simple_comet
            
--http-port=<HTTP server port>
--http-timeout=<HTTP timeout in seconds>
--session-timeout=<session timeout in seconds>
--messages-per-channel=<default max messages per channel>
--quote-jsonp
    """
    exit(0)
    

def parse_opt(config, opt):
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
        
    return config
    

def get_config():
    config = Config()
    args = sys.argv[1: ]
    opts = [ "http-port=", "http-timeout=", "session-timeout=",
             "max-messages-per-channel=", "quote-jsonp" ]
    try:
        optlist, args = getopt(args, None, opts)
    except GetoptError:        
        help()
    
    for opt in optlist:
        config = parse_opt(config, opt)
        
    return config


def main():
    config = get_config()
    comet_server = CometServer(reactor, config)
    site = server.Site(comet_server, timeout = config.http_timeout)
    reactor.listenTCP(config.http_port, site)
    reactor.run()


if __name__ == '__main__':
    main()
