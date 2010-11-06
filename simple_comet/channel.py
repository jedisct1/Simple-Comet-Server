
from config import *
import time
from collections import deque
from twisted.internet import reactor


class Channel(object):
    id = property(lambda self: self._id)
    max_messages = property(lambda self: self._max_messages)
    
    
    def __init__(self, id, max_messages, timeout_cb, use_sessions = False):
        self._id = id
        assert(max_messages > 0)
        self._max_messages = max_messages
        self.timeout_cb = timeout_cb
        self.use_sessions = use_sessions
        self.messages = deque()
        self._timeout_delayed_call = \
            reactor.callLater(10, self.timeout)

    
    def push_message_content(self, message_id, content):
        message = { "id": message_id, "ts": int(time.time()),
                    "content": content }
        while len(self.messages) >= self.max_messages:
            self.messages.pop()
        
        self.messages.appendleft(message)

        
    def messages_since(self, message_id):
        found_messages = filter(lambda message: message["id"] > message_id,
                                self.messages)
        return found_messages

    
    def cancel_timeout_delayed_call(self):
        if self._timeout_delayed_call != None and \
            self._timeout_delayed_call.active():
            self._timeout_delayed_call.cancel()        
        
        self._timeout_delayed_call = None
    
    
    def timeout(self):
        self.cancel_timeout_delayed_call()
        self.timeout_cb(self._id, self.teardown)
        
        
    def teardown(self):
        self.cancel_timeout_delayed_call()
        
    
