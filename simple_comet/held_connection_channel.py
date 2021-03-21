class HeldConnectionChannel(object):
    def __init__(self):
        self._held_connection_id_to_channels_ids = dict()
        self._channel_id_to_held_connections = dict()
        self._connection_id_to_connection = dict()

    held_connections_count = property(
        lambda self: len(self._held_connection_id_to_channels_ids)
    )

    def register_held_connection_for_channels_ids(self, connection, channels_ids):
        connection_id = connection.id
        self._connection_id_to_connection[connection_id] = connection

        if connection_id not in self._held_connection_id_to_channels_ids:
            self._held_connection_id_to_channels_ids[connection_id] = set()

        for channel_id in channels_ids:
            self._held_connection_id_to_channels_ids[connection_id].add(channel_id)

            if channel_id not in self._channel_id_to_held_connections:
                self._channel_id_to_held_connections[channel_id] = set()

            self._channel_id_to_held_connections[channel_id].add(connection_id)

    def remove_held_connection_id(self, connection_id):
        if connection_id not in self._held_connection_id_to_channels_ids:
            return

        for channel_id in self._held_connection_id_to_channels_ids[connection_id]:
            self._channel_id_to_held_connections[channel_id].remove(connection_id)

        del self._held_connection_id_to_channels_ids[connection_id]

    def channel_id_to_held_connections(self, channel_id):
        if channel_id not in self._channel_id_to_held_connections:
            return list()

        return [
            self._connection_id_to_connection[connection_id]
            for connection_id in self._channel_id_to_held_connections[channel_id]
        ]

    def remove_channel_id(self, channel_id):
        if channel_id not in self._channel_id_to_held_connections:
            return

        held_connections = self._channel_id_to_held_connections[channel_id]
        for connection_id in [
            held_connection.id for held_connection in held_connections
        ]:
            del self._held_connection_id_to_channels_ids[connection_id]

        del self._channel_id_to_held_connections[channel_id]
