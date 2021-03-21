import time
from twisted.web import resource
from twisted.web.server import NOT_DONE_YET
from .connection import Connection
from .client_channel import ClientChannel, ExistingChannelError, ExistingClientError
from .held_connection_channel import HeldConnectionChannel


class CometServer(resource.Resource):
    isLeaf = True

    current_message_id = property(lambda self: self._current_message_id)
    config = property(lambda self: self._config)

    def __init__(self, config):
        resource.Resource.__init__(self)
        self._config = config
        self.client_channel = ClientChannel(config)
        self.held_connection_channel = HeldConnectionChannel()
        self._current_message_id = int(time.time() * config.max_messages_per_second)
        self._current_connection_id = 0
        self.comet_server = self

    def render_POST(self, request):
        connection_id = self.pop_connection_id()
        connection = Connection(self, request, connection_id)
        try:
            format = connection.get_format(self.config.clients_uri_path)
        except ValueError as e:
            return connection.error(-1, str(e))

        if format:
            return self.register_client(connection)

        try:
            (channel_id, format) = connection.get_channel_id_and_format()
        except ValueError as e:
            return connection.error(-1, str(e))

        if not channel_id:
            if b"channel_id" not in request.args:
                return connection.error(-1, "Missing channel id")

            (channel_id,) = request.args[b"channel_id"]
            channel_id = channel_id.decode("utf-8")
            use_sessions = False
            if b"use_sessions" in request.args:
                use_sessions = bool(request.args[b"use_sessions"][0])

            if b"max_messages" in request.args:
                try:
                    max_messages = int(request.args[b"max_messages"][0])
                    if max_messages < 1:
                        raise ValueError("Channels should at least store one message")

                except ValueError:
                    return connection.error(-1, "Invalid max messages value")
            else:
                max_messages = self.config.default_max_messages_per_channel

            return self.register_channel_id(
                connection=connection,
                channel_id=channel_id,
                max_messages=max_messages,
                use_sessions=use_sessions,
            )

        try:
            channel = self.client_channel.channel_id_to_channel(channel_id)
        except KeyError:
            return connection.error(-2, "Nonexistent channel")

        if b"content" not in request.args:
            return connection.error(-1, "Missing content")

        (content,) = request.args[b"content"]
        content = content.decode("utf-8")
        message_id = self.pop_message_id()
        channel.push_message_content(message_id, content)
        held_connections = self.held_connection_channel.channel_id_to_held_connections(
            channel_id
        )
        new_messages = channel.messages_since(self.current_message_id - 1)
        channels_messages = {channel_id: new_messages}
        for held_connection in held_connections:
            result = held_connection.success(
                {
                    "messages": channels_messages,
                    "since": held_connection.meta["since"],
                    "last_id": self.current_message_id,
                }
            )
            held_connection.send_cache_headers()
            held_connection.delayed_reply(result)
            self.held_connection_channel.remove_held_connection_id(held_connection.id)

        return connection.success({"message_id": message_id})

    def render_GET(self, request):
        connection_id = self.pop_connection_id()
        connection = Connection(self, request, connection_id)
        if self.config.enable_status:
            try:
                format = connection.get_format(self.config.status_uri_path)
            except ValueError as e:
                return connection.error(-1, str(e))

            if format:
                return self.show_status(connection)

        try:
            (channels_ids_s, format) = connection.get_channel_id_and_format()
        except ValueError as e:
            return connection.error(-1, str(e))

        if not channels_ids_s:
            return connection.error(-2, "No channels")
        channels_ids = channels_ids_s.split(self.config.channels_sep)
        if not channels_ids:
            return connection.error(-2, "Empty channels list")

        return self.handle_channels_read(connection, channels_ids)

    def render_DELETE(self, request):
        connection_id = self.pop_connection_id()
        connection = Connection(self, request, connection_id)
        try:
            (channel_id, _format) = connection.get_channel_id_and_format()
        except ValueError as e:
            return connection.error(-1, str(e))

        removed = self.remove_channel_id(channel_id)

        return connection.success(
            {"channel_id": channel_id, "removed": removed}, return_code=int(removed) + 1
        )

    def pop_message_id(self):
        self._current_message_id = self._current_message_id + 1
        return self.current_message_id

    def pop_connection_id(self):
        self._current_connection_id = self._current_connection_id + 1
        return self._current_connection_id

    def handle_channels_read(self, connection, channels_ids):
        request = connection.request
        since = 0
        if b"since" in request.args:
            try:
                since = int(request.args[b"since"][0])
            except ValueError:
                pass

            since = min(since, self._current_message_id)

        if b"client_id" not in request.args:
            client_id = None
            client = None
        else:
            (client_id,) = request.args[b"client_id"]
            client_id = client_id.decode("utf-8")
            if not client_id:
                return connection.error(-1, "Missing client_id")

            try:
                client = self.client_channel.client_id_to_client(client_id)
            except KeyError:
                return connection.error(-3, "Unregistered client_id")

            client.ping()

        authorized_channels_ids = list()
        for channel_id in channels_ids:
            try:
                channel = self.client_channel.channel_id_to_channel(channel_id)
            except KeyError:
                continue

            if channel.use_sessions is True and client_id is None:
                continue

            authorized_channels_ids.append(channel_id)

            if client_id:
                self.client_channel.register_client_id_for_channel_id(
                    client_id, channel_id
                )

        if not authorized_channels_ids:
            return connection.error(-2, "No valid channels")

        channels_messages = dict()
        empty = True

        for channel_id in authorized_channels_ids:
            try:
                channel = self.client_channel.channel_id_to_channel(channel_id)
            except KeyError:
                continue

            new_messages = channel.messages_since(since)
            channels_messages[channel_id] = new_messages
            if new_messages:
                empty = False

        if not empty:
            connection.send_cache_headers()
            return connection.success(
                {
                    "messages": channels_messages,
                    "since": since,
                    "last_id": self.current_message_id,
                }
            )

        connection.meta = {"since": since}
        self.held_connection_channel.register_held_connection_for_channels_ids(
            connection, authorized_channels_ids
        )

        request.notifyFinish().addBoth(self.connection_finished, connection.id)

        return NOT_DONE_YET

    def connection_finished(self, failure, connection_id):
        self.held_connection_channel.remove_held_connection_id(connection_id)

    def register_channel_id(self, connection, channel_id, max_messages, use_sessions):
        try:
            self.client_channel.register_channel_id(
                channel_id, max_messages, use_sessions
            )
        except ExistingChannelError as e:
            return connection.error(-2, str(e))

        return connection.success({"channel_id": channel_id})

    def remove_channel_id(self, channel_id):
        try:
            self.client_channel.channel_id_to_channel(channel_id)
        except KeyError:
            return False

        self.client_channel.remove_channel_id(channel_id)
        return True

    def client_timeout_cb(self, client, teardown_cb):
        _empty_channels_ids = (
            self.client_channel.remove_client_id_and_return_empty_channels_ids(
                client.id
            )
        )
        teardown_cb()

    def register_client(self, connection):
        request = connection.request
        if b"client_id" not in request.args:
            return connection.error(-1, "Missing client id")
        (client_id,) = request.args[b"client_id"]
        client_id = client_id.decode("utf-8")

        try:
            self.client_channel.register_client_id(
                self, client_id, self.client_timeout_cb
            )
        except ExistingClientError as e:
            return connection.error(-2, str(e))

        return connection.success({"client_id": client_id})

    def show_status(self, connection):
        channels = self.client_channel.channel_id_to_clients_ids
        clients = self.client_channel.client_id_to_channel_id_to_channels_ids
        held_connections_count = self.held_connection_channel.held_connections_count

        status = {
            "channels": list(channels.keys()),
            "clients": list(clients.keys()),
            "held_connections_count": held_connections_count,
        }

        return connection.success({"status": status})
