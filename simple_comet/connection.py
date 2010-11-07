
from config import *
from wsgiref.handlers import format_date_time
from datetime import datetime, timedelta
from time import mktime
import urllib
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
        path = urllib.unquote(self._request.path)
        channels_uri_path = self.comet_server.config.channels_uri_path
        if not path.startswith(channels_uri_path):
            raise ValueError("Missing %r prefix" % channels_uri_path)
        
        channel_id_and_format_s = path[len(channels_uri_path):]
        if channel_id_and_format_s.endswith(".json"):
            channel_id = channel_id_and_format_s[: -len(".json")]
            self.format = "json"            
        elif channel_id_and_format_s.endswith(".jsonp"):
            channel_id = channel_id_and_format_s[: -len(".jsonp")]
            self.format = "jsonp"           
        else:
            raise ValueError("Unknown output format")
        
        if channel_id != "":
            assert(channel_id[0] == "/")
            channel_id = channel_id[1:]         
        else:
            channel_id = None
        
        return (channel_id, self.format)

    
    def get_format(self, wanted_path):
        path = self._request.path
        if path == wanted_path + ".json":
            self.format = "json"
        elif path == wanted_path + ".jsonp":
            self.format = "jsonp"
        elif path.startswith(wanted_path):
            raise ValueError("Unknown output format")
        else:
            return None
        
        return self.format
    
    
    def send_cache_headers(self):
        http_cache_age = self.comet_server.config.http_cache_age
        cache_age_s = str(http_cache_age)
        self._request.setHeader("Cache-Control",
          "private, must-revalidate, proxy-revalidate, " \
          "max-age=" + cache_age_s + ", " \
          "s-max-age=" + cache_age_s + ", " \
          "stale-while-revalidate=" + cache_age_s + ", " \
          "stale-if-error=86400")
        expire_tt = (datetime.now() + timedelta(seconds = http_cache_age)).timetuple()
        expire_ts = mktime(expire_tt)
        self._request.setHeader("Expires", format_date_time(expire_ts))

        
    def render(self, obj):
        config = self.comet_server.config
        json_obj = json.dumps(obj)
        if self.format == "jsonp":
            self._request.setHeader("Content-Type", "application/javascript")
            jsonp_cb = config.default_jsonp_cb
            if "cb" in self._request.args:
                (jsonp_cb,) = self._request.args["cb"]
                
            if jsonp_cb.find(config.jsonp_required_substr) < 0:
                return "/* incomplete JSONP callback name */"
            
            if not re.search("^[a-z_]+[a-z0-9_.]*$", jsonp_cb, re.IGNORECASE):
                return "/* invalid JSONP callback name */"

            jsonp_ret = jsonp_cb + "(" + json_obj + ");"                
        else:
            assert(config.default_format == "json")
            self._request.setHeader("Content-Type", "application/json")
            
            if config.quote_json:
                json_ret = "/*-secure- " + json_obj + " */"
            else:
                json_ret = json_obj
        
        return json_obj


    def error(self, return_code, message):
        assert(return_code < 0)
        return self.render({ "return_code": return_code,
                             "error_message": message })

                            
    def success(self, obj = { }, return_code = 1, error_message = ""):
        assert(return_code > 0)
        obj["return_code"] = return_code
        obj["error_message"] = error_message
        return self.render(obj)

    
    def delayed_reply(self, result):
        self._request.write(result)
        self._request.finish()


