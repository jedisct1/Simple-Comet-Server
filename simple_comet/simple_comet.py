
from config import Config
from twisted.web import server

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
    
from twisted.internet import reactor
from comet_server import CometServer
import sys

        
def main():
    args = sys.argv[1: ]
    config = Config(args)
    comet_server = CometServer(config)
    site = server.Site(comet_server, timeout = config.http_timeout)
    if config.http_port != None:
        reactor.listenTCP(config.http_port, site)
        
    if config.unix_socket_path != None:
        reactor.listenUNIX(config.unix_socket_path, site)
        
    reactor.run()


if __name__ == '__main__':
    main()
