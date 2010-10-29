
import cgi
import time
import re
try:
    import json
except ImportError:
    import simplejson as json

from twisted.web import server, resource, http
from twisted.web.server import NOT_DONE_YET
from twisted.internet import reactor
from collections import deque
from pprint import pprint
from config import *
from connection import Connection
from channel import Channel
from client import Client
from client_channel import ClientChannel, \
    ExistingChannelError, ExistingClientError
from held_connection_channel import HeldConnectionChannel


class CometServer(object, resource.Resource):
    isLeaf = True

    current_message_id = property(lambda self: self._current_message_id)
    
    
    def __init__(self, reactor):
        self.client_channel = ClientChannel()
        self.held_connection_channel = HeldConnectionChannel()
        self._current_message_id = int(time.time() * MESSAGES_PER_SECOND)
        self._current_connection_id = 0
        self._reactor = reactor
        self.comet_server = self

        
    def pop_message_id(self):
        self._current_message_id = self._current_message_id + 1
        return self.current_message_id
        
    
    def pop_connection_id(self):
        self._current_connection_id = self._current_connection_id + 1
        return self._current_connection_id
        
                
    def render_POST(self, request):
        connection_id = self.pop_connection_id()
        connection = Connection(request, connection_id)
        try:            
            (channel_id, format) = connection.get_channel_id_and_format()       
        except ValueError as e:
            return connection.error(-1, str(e))
        
        if not channel_id:
            if not "channel_id" in request.args:
                return connection.error(-1, "Missing channel id")
                        
            channel_id = request.args["channel_id"][0]
            use_sessions = "use_sessions" in request.args
            
            return self.register_channel_id(connection, channel_id, use_sessions)

        try:
            channel = self.client_channel.channel_id_to_channel(channel_id)
        except KeyError:
            return connection.error(-2, "Nonexistent channel")
        
        if not "content" in request.args:
            return connection.error(-1, "Missing content")
        
        content = request.args["content"][0]
        message_id = self.pop_message_id()
        channel.push_message_content(message_id, content)
        held_connections = self.held_connection_channel.channel_id_to_held_connections(channel_id)
        new_messages = channel.messages_since(self.current_message_id - 1)
        channels_messages = { channel_id: new_messages }
        for held_connection in held_connections:
            result = held_connection.success({ "messages": channels_messages,
                                               "last_id": self.current_message_id })
            held_connection.send_cache_headers()
            held_connection.delayed_reply(result)
            self.held_connection_channel.remove_held_connection_id(held_connection.id)

        return connection.success({ "message_id": message_id })
    
    
    def handle_channels_read(self, connection, channels_ids):
        request = connection.request
        since = 0
        if "since" in request.args:
            since = int(request.args["since"][0])           
            since = min(since, self._current_message_id)
            
        if not "client_id" in request.args:
            return connection.error(-1, "Missing client_id")
        
        client_id = request.args["client_id"][0]
        
        try:
            client = self.client_channel.client_id_to_client(client_id)
        except KeyError:
            return connection.error(-3, "Unregistered client_id")

        client.ping()
        channels_data = dict()
        for channel_id in channels_ids:
            try:
                channel = self.client_channel.channel_id_to_channel(channel_id)
            except KeyError:
                channels_data[channel_id] = list()
                continue
            
            self.client_channel.register_client_id_for_channel_id(client_id, channel_id)
        
        channels_messages = dict()
        empty = True

        for channel_id in channels_ids:
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
            return connection.success({ "messages": channels_messages,
                                        "last_id": self.current_message_id })
                                        
        self.held_connection_channel. \
            register_held_connection_for_channels_ids(connection, channels_ids)

        request.notifyFinish().addBoth(self.connection_finished, connection.id)
            
        return NOT_DONE_YET        
        

    def render_GET(self, request):
        connection_id = self.pop_connection_id()        
        connection = Connection(request, connection_id)
        try:            
            format = connection.get_format(HANDSHAKE_URI_PATH)
        except ValueError as e:
            return connection.error(-1, str(e))
        
        if format:
            return self.handshake(connection)
        
        try:
            (channels_ids_s, format) = connection.get_channel_id_and_format()
        except ValueError as e:
            return connection.error(-1, str(e))     

        channels_ids = channels_ids_s.split(CHANNELS_SEP)
        if not channels_ids:
            return connection.error(-2, "No channels")
        
        return self.handle_channels_read(connection, channels_ids)

    
    def connection_finished(self, failure, connection_id):
        self.held_connection_channel.remove_held_connection_id(connection_id)
    
        
    def register_channel_id(self, connection, channel_id):
        try:
            self.client_channel.register_channel_id(channel_id)         
        except ExistingChannelError as e:
            return connection.error(-2, str(e))
        
        return connection.success({ "channel_id": channel_id })
    
    
    def client_timeout_cb(self, client, teardown_cb):
        self.client_channel.remove_client_id(client.id)     
        teardown_cb()
    
        
    def handshake(self, connection):
        client_id = str("1")
        try:
            self.client_channel.register_client_id(client_id, self.client_timeout_cb)
        except ExistingClientError as e:
            return connection.error(-2, str(e))
        
        return connection.success({ "client_id": client_id })
        
