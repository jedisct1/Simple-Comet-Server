
def _install_reactors():
    reactors_names = [ "kqreactor", "epollreactor", "pollreactor" ]
    for reactor_name in reactors_names:
        try:
            exec("from twisted.internet import %s as _reactor" % reactor_name)
            _reactor.install()
            break
        except AssertionError:
            break
        except Exception:
            pass
        

from config import Config
from twisted.web import server
_install_reactors()
from twisted.internet import reactor
from comet_server import CometServer
import sys

        
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
