from wsgiref.handlers import format_date_time
from datetime import datetime, timedelta
from time import mktime
import urllib.request
import urllib.parse
import urllib.error
import re


try:
    import json
except ImportError:
    import simplejson as json


class Connection(object):
    id = property(lambda self: self._id)
    request = property(lambda self: self._request)
    comet_server = property(lambda self: self._comet_server)

    def __init__(self, comet_server, request, id):
        self._comet_server = comet_server
        self._request = request
        self.format = None
        self._id = id
        self._meta = None

    def get_channel_id_and_format(self):
        path = urllib.parse.unquote(self._request.path).encode("utf-8")
        channels_uri_path = self.comet_server.config.channels_uri_path
        if not path.startswith(channels_uri_path):
            raise ValueError("Missing %r prefix" % channels_uri_path.decode("utf-8"))

        channel_id_and_format_s = path[len(channels_uri_path) :]
        if channel_id_and_format_s.endswith(b".json"):
            channel_id = channel_id_and_format_s[: -len(b".json")].decode("utf-8")
            self.format = b"json"
        elif channel_id_and_format_s.endswith(b".jsonp"):
            channel_id = channel_id_and_format_s[: -len(b".jsonp")].decode("utf-8")
            self.format = b"jsonp"
        else:
            raise ValueError("Unknown output format")

        if channel_id != "":
            assert channel_id[0:1] == "/"
            channel_id = channel_id[1:]
        else:
            channel_id = None

        return (channel_id, self.format)

    def get_format(self, wanted_path):
        path = self._request.path
        if path == wanted_path + b".json":
            self.format = b"json"
        elif path == wanted_path + b".jsonp":
            self.format = b"jsonp"
        elif path.startswith(wanted_path):
            raise ValueError("Unknown output format")
        else:
            return None

        return self.format

    def send_cache_headers(self):
        http_cache_age = self.comet_server.config.http_cache_age
        cache_age_s = str(http_cache_age)
        self._request.setHeader(
            "Cache-Control",
            "private, must-revalidate, proxy-revalidate, "
            "max-age=" + cache_age_s + ", "
            "s-max-age=" + cache_age_s + ", "
            "stale-while-revalidate=" + cache_age_s + ", "
            "stale-if-error=86400",
        )
        expire_tt = (datetime.now() + timedelta(seconds=http_cache_age)).timetuple()
        expire_ts = mktime(expire_tt)
        self._request.setHeader("Expires", format_date_time(expire_ts))

    def render(self, obj):
        config = self.comet_server.config
        json_obj = json.dumps(obj)
        if self.format == b"jsonp":
            self._request.setHeader("Content-Type", "application/javascript")
            jsonp_cb = config.default_jsonp_cb
            if "cb" in self._request.args:
                (jsonp_cb,) = self._request.args["cb"]

            if jsonp_cb.find(config.jsonp_required_substr) < 0:
                return b"/* incomplete JSONP callback name */"

            if not re.search("^[a-z_]+[a-z0-9_.]*$", jsonp_cb, re.IGNORECASE):
                return b"/* invalid JSONP callback name */"

            return (jsonp_cb + "(" + json_obj + ");").encode("utf-8")
        else:
            assert config.default_format == b"json"
            self._request.setHeader("Content-Type", "application/json")

            if config.quote_json:
                return ("/*-secure- " + json_obj + " */").encode("utf-8")
            else:
                return json_obj.encode("utf-8")

    def error(self, return_code, message):
        assert return_code < 0
        return self.render({"return_code": return_code, "error_message": message})

    def success(self, obj={}, return_code=1, error_message=""):
        assert return_code > 0
        obj["return_code"] = return_code
        obj["error_message"] = error_message
        return self.render(obj)

    def delayed_reply(self, result):
        self._request.write(result)
        self._request.finish()
