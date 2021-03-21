from .channel import Channel
from .client import Client


class ExistingChannelError(Exception):
    pass


class ExistingClientError(Exception):
    pass


class ClientChannel(object):
    def __init__(self, config):
        self._config = config
        self._channel_id_to_channel = dict()
        self._client_id_to_client = dict()
        self._channel_id_to_clients_ids = dict()
        self._client_id_to_channels_ids = dict()

    channel_id_to_clients_ids = property(lambda self: self._channel_id_to_clients_ids)

    client_id_to_channel_id_to_channels_ids = property(
        lambda self: self._client_id_to_channels_ids
    )

    def register_channel_id(self, channel_id, max_messages, use_sessions):
        if channel_id in self._channel_id_to_channel:
            raise ExistingChannelError("Channel already exists")

        channel = Channel(
            id=channel_id,
            max_messages=max_messages,
            timeout=self._config.inactive_channel_timeout,
            timeout_cb=self.channel_timeout_cb,
            use_sessions=use_sessions,
        )
        self._channel_id_to_channel[channel_id] = channel
        self._channel_id_to_clients_ids[channel_id] = set()

    def register_client_id(self, comet_server, client_id, timeout_cb):
        if client_id in self._client_id_to_client:
            raise ExistingClientError("Client already exists")

        client = Client(
            comet_server=comet_server, id=client_id, timeout_cb=timeout_cb, meta=None
        )
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

        del self._client_id_to_client[client_id]
        del self._client_id_to_channels_ids[client_id]

        return empty_channels

    def remove_channel_id(self, channel_id):
        if channel_id in self._channel_id_to_clients_ids:
            for client_id in self._channel_id_to_clients_ids[channel_id]:
                self._client_id_to_channels_ids[client_id].remove(channel_id)

        if channel_id in self._channel_id_to_clients_ids:
            del self._channel_id_to_clients_ids[channel_id]

        if channel_id in self._channel_id_to_channel:
            channel = self._channel_id_to_channel[channel_id]
            del self._channel_id_to_channel[channel_id]
            channel.teardown()

    def channel_timeout_cb(self, channel_id, teardown_cb):
        if (
            channel_id in self._channel_id_to_clients_ids
            and self._channel_id_to_clients_ids[channel_id]
        ):
            return

        self.remove_channel_id(channel_id)
        teardown_cb()
