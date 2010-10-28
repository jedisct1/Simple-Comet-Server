
import time
from collections import deque


class Channel(object):
    id = property(lambda self: self._id)
    
    
    def __init__(self, id):
        self._id = id
        self.messages = deque()            
        
    
    def push_message_content(self, message_id, content):
        message = { "id": message_id, "ts": int(time.time()), "content": content }      
        self.messages.appendleft(message)

        
    def messages_since(self, message_id):
        found_messages = filter(lambda message: message["id"] > message_id,
                                self.messages)
        return found_messages
