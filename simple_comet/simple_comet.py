
from config import *
from twisted.internet import reactor
from twisted.web import server, resource, http
from comet_server import CometServer
import sys

def main():
    args = sys.argv[1: ]
    config = Config(args)
    comet_server = CometServer(reactor, config)
    site = server.Site(comet_server, timeout = config.http_timeout)
    reactor.listenTCP(config.http_port, site)
    reactor.run()


if __name__ == '__main__':
    main()
