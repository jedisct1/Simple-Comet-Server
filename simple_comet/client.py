
from config import *
from twisted.internet import reactor


class Client(object):
    id = property(lambda self: self._id)
    
    
    def __init__(self, id, timeout_cb):
        self._id = id
        self._timeout_delayed_call = None
        self.timeout_cb = timeout_cb
        self.channels = dict()
        self.ping()
    
        
    def ping(self):
        if self._timeout_delayed_call == None or not self._timeout_delayed_call.active():
            self._timeout_delayed_call = reactor.callLater(CLIENT_TIMEOUT, self.timeout)
        else:
            self._timeout_delayed_call.reset(CLIENT_TIMEOUT)
        
            
    def cancel_timeout_delayed_call(self):
        if self._timeout_delayed_call != None and self._timeout_delayed_call.active():
            self._timeout_delayed_call.cancel()
            
        self.timeout_delayed_call = None

        
    def timeout(self):
        self.cancel_timeout_delayed_call()
        self.timeout_cb(self, self.teardown)
        
        
    def teardown(self):
        self.cancel_timeout_delayed_call()
        
