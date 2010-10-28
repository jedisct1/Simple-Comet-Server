
class HeldConnectionChannel(object):
    def __init__(self):
        self._held_connection_id_to_channels_ids = dict()
        self._channel_id_to_held_connections = dict()
        self._connection_id_to_connection = dict()
        
    def register_held_connection_for_channels_ids(self, connection, channels_ids):
        connection_id = connection.id
        self._connection_id_to_connection[connection_id] = connection
        
        if not connection_id in self._held_connection_id_to_channels_ids:
            self._held_connection_id_to_channels_ids[connection_id] = set()
        
        for channel_id in channels_ids:
            self._held_connection_id_to_channels_ids[connection_id].add(channel_id)
            
            if not channel_id in self._channel_id_to_held_connections:
                self._channel_id_to_held_connections[channel_id] = set()
                
            self._channel_id_to_held_connections[channel_id].add(connection_id)

    
    def remove_held_connection_id(self, connection_id):
        if not connection_id in self._held_connection_id_to_channels_ids:
            return
        
        for channel_id in self._held_connection_id_to_channels_ids[connection_id]:
            self._channel_id_to_held_connections[channel_id].remove(connection_id)
            
        self._held_connection_id_to_channels_ids.pop(connection_id)
        
        
    def channel_id_to_held_connections(self, channel_id):
        if channel_id not in self._channel_id_to_held_connections:
            return list()
        
        return [ self._connection_id_to_connection[connection_id] \
                 for connection_id \
                 in self._channel_id_to_held_connections[channel_id] ]
