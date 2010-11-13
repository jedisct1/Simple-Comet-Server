
from config import Config
from twisted.internet import reactor

        

from twisted.web import server
from comet_server import CometServer
import sys

def _install_reactors():
    reactors = [ "kqreactor", "epollreactor", "pollreactor" ]
    for reactor in reactors:
        try:
            exec("from twisted.internet import %s as _reactor" % reactor)
            _reactor.install()
            break
        except AssertionError:
            break
        except Exception:
            pass


def main():
    args = sys.argv[1: ]
    config = Config(args)
    _install_reactors()
    comet_server = CometServer(config)
    site = server.Site(comet_server, timeout = config.http_timeout)
    reactor.listenTCP(config.http_port, site)
    reactor.run()


if __name__ == '__main__':
    main()
