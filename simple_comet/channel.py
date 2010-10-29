
from config import *
import time
from collections import deque


class Channel(object):
    id = property(lambda self: self._id)
    
    
    def __init__(self, id, use_sessions = False):
        self._id = id
        self.use_sessions = use_sessions
        self.messages = deque()
        
    
    def push_message_content(self, message_id, content):
        message = { "id": message_id, "ts": int(time.time()), "content": content }
        while len(self.messages) >= DEFAULT_MAX_MESSAGES_PER_CHANNEL:
            self.messages.pop()
        
        self.messages.appendleft(message)

        
    def messages_since(self, message_id):
        found_messages = filter(lambda message: message["id"] > message_id,
                                self.messages)
        return found_messages
