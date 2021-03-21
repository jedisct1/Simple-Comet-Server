from twisted.internet import reactor


class Client(object):
    id = property(lambda self: self._id)
    meta = property(lambda self: self._meta)
    comet_server = property(lambda self: self._comet_server)

    def __init__(self, comet_server, id, timeout_cb, meta=None):
        self._comet_server = comet_server
        self._id = id
        self._meta = meta
        self._timeout_delayed_call = None
        self.timeout_cb = timeout_cb
        self.channels = dict()
        self.ping()

    def ping(self):
        config = self.comet_server.config
        if (
            self._timeout_delayed_call is None
            or not self._timeout_delayed_call.active()
        ):
            self._timeout_delayed_call = reactor.callLater(
                config.client_session_timeout, self.timeout
            )
        else:
            self._timeout_delayed_call.reset(config.client_session_timeout)

    def cancel_timeout_delayed_call(self):
        if (
            self._timeout_delayed_call is not None
            and self._timeout_delayed_call.active()
        ):
            self._timeout_delayed_call.cancel()

        self._timeout_delayed_call = None

    def timeout(self):
        self.cancel_timeout_delayed_call()
        self.timeout_cb(self, self.teardown)

    def teardown(self):
        self.cancel_timeout_delayed_call()
