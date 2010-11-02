
from channel import Channel
from client import Client


class ExistingChannelError(Exception):
    pass


class ExistingClientError(Exception):
    pass

                            
class ClientChannel(object):
    def __init__(self):
        self._channel_id_to_channel = dict()
        self._client_id_to_client = dict()
        self._channel_id_to_clients_ids = dict()
        self._client_id_to_channels_ids = dict()

        
    def register_channel_id(self, channel_id, max_messages, use_sessions):
        if channel_id in self._channel_id_to_channel:
            raise ExistingChannelError("Channel already exists")

        channel = Channel(channel_id, max_messages, use_sessions)
        self._channel_id_to_channel[channel_id] = channel
        self._channel_id_to_clients_ids[channel_id] = set()
        
        
    def register_client_id(self, comet_server, client_id, timeout_cb):
        if client_id in self._client_id_to_client:
            raise ExistingClientError("Client already exists")
        
        client = Client(comet_server, client_id, timeout_cb)
        self._client_id_to_client[client_id] = client
        self._client_id_to_channels_ids[client_id] = set()

        
    def channel_id_to_channel(self, channel_id):
        return self._channel_id_to_channel[channel_id]


    def client_id_to_client(self, client_id):
        return self._client_id_to_client[client_id]

    
    def register_client_id_for_channel_id(self, client_id, channel_id):
        self._channel_id_to_clients_ids[channel_id].add(client_id)
        self._client_id_to_channels_ids[client_id].add(channel_id)

    
    def remove_client_id_and_return_empty_channels_ids(self, client_id):
        empty_channels = set()
        for channel_id in self._client_id_to_channels_ids[client_id]:
            self._channel_id_to_clients_ids[channel_id].remove(client_id)
            if len(self._channel_id_to_clients_ids[channel_id]) == 0:
                empty_channels.add(channel_id)
        
        self._client_id_to_client.pop(client_id)
        self._client_id_to_channels_ids.pop(client_id)
        return empty_channels


    def remove_channel_id(self, channel_id):
        for client_id in self._channel_id_to_clients_ids[channel_id]:
            self._client_id_to_channels_ids[client_id].remove(channel_id)
        
        self._channel_id_to_channel.pop(channel_id)
        self._channel_id_to_clients_ids.pop(channel_id)

    
    
