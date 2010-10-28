
from config import *
from twisted.internet import reactor
from twisted.web import server, resource, http
from comet_server import CometServer

def main():
    comet_server = CometServer(reactor)
    site = server.Site(comet_server)
    reactor.listenTCP(DEFAULT_PORT, site)
    reactor.run()


if __name__ == '__main__':
    main()
