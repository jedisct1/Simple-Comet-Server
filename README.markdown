A simple COMET server
=====================

This is a simple HTTP long-polling server.

With intentionally no support for Websockets nor Bayeux.

But the client-side Javascript library weights only 1 Kb, including
support for multiple channels and cross-domain requests.

It should work just fine on most web browsers, including legacy ones and
mobile browsers.


Installation
------------

The server requires Python and the Twisted framework.

It can be installed the boring way:

    git clone git://github.com/jedisct1/Simple-Comet-Server.git
    cd Simple-Comet-Server
    sudo python setup.py install    
    
Using simple_comet as a backend for a frontend server like Nginx is
highly recommended.
    

Server switches
---------------

`simple_comet`
    
    --http-port=<HTTP server port> (default=8080)

Change the HTTP port the server will listen to.

    --http-timeout=<HTTP timeout in seconds> (default=30)

Drop inactive connections after this many seconds.

    --session-timeout=<session timeout in seconds> (default=60)

Clear sessions after this many seconds.

    --inactive-channel-timeout=<inactive channel timeout> (default=90)

Remove channels with no clients after this many seconds.

    --messages-per-channel=<default max messages per channel> (default=100)
    
The default number of messages to keep in every channel. When the
queue is full, the oldest message will get dropped in order to make
space for new messages.
    
    --quote-json

Encapsulate JSON responses with /*-secure- ... */ comments.

    --enable-status

Enable /stats.json in order to monitor activity.


REST API
--------

For every resource, a `.json` suffix returns the result as a
JSON-serialized object, while a `.jsonp` suffix returns a reply
suitable for a JSON-P request.

The default callback for JSON-P requests is `_JSONP_comet_cb()`.
It can be changed through the value of a `cb` variable added to the
query string, but the name must start with `_JSONP_`.


* **Registering a channel**

Your server-side application should probably handle this, not the
client.

    Method: POST
    URI: http://$HOST:$PORT/channels.json
    Payload:
    channel_id=(name of the new channel)
    use_sessions=1: only registered clients can join the channel
    max_messages=(non-default number of retained messages)
    
  
* **Pushing data to a channel**

Store a new message and forward it to subscribers.

    Method: POST
    URI: http://$HOST:$PORT/channels/(channel name).json
    Payload:
    content=(message content)


* **Registering a client**

Your server-side application should probably handle this, not the
client.
Registered clients can join non-anonymous channels.
Registering a client is not required in order to subscribe to
anonymous channels.

    Method: POST
    URI: http://$HOST:$PORT/clients.json
    Payload:
    client_id=(unique client identifier)


* **Monitoring the server**

Only available if --enable-status has been enabled.

    Method: GET
    URI: http://$HOST:$PORT/status.json


* **Reading data from channels**

This should be sent by your server-side application.

    Method: `GET`
    URI: `http://$HOST:$PORT/channels/(channels list).json`
    Query string:
    client_id=(client identifier): only required for non-anonymous channels
    since=(identifier of the last read frame)
   
Multiple channels can be subscribed to, and anonymous and non-anonymous
channels can be mixed. Just use a pipe (`%7C`) as a delimiter.

The reply looks like:

    { "since": 0,
      "messages": {
        "channelA": [
          { "content": "message1",
            "id": 128916015846785,
            "ts": 1289160231
          }
        ],
        "channelB": [
          { "content": "message1",
            "id": 128916015846786,
            "ts": 1289160235
          },
          { "content": "message2",
            "id": 128916015846787,
            "ts": 1289160237
          }
        ]        
      },
      "return_code": 1,
      "error_message": "",
      "last_id": 128916015846785
    }

`last_id` is the identifier of the last frame. The following request
should include it as the value for `since`.
The first request may omit this or use 0.


Javascript API
--------------

The Javascript library (`client/simple-comet.js`) is designed to query a single server, through JSON-P.

    SimpleComet.subscribe(url, callback, client_id)
    
`client_id` is only required in order to subscribe to non-anonymous
channels.

The callback function will be called every time a watched channel will
be updated.

