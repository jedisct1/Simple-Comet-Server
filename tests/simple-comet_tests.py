
from nose.tools import *
import urllib
import urllib2
try:
    import json
except ImportError:
    import simplejson as json

from simple_comet import main
    

BASE_URI = "http://127.0.0.1:8080"


def setup():
    pass


def teardown():
    pass


def _issue_command(uri_part, data, cb, method = None):
    if data:
        if not method:
            method = "POST"

        _data = urllib.urlencode(data)            
        request = urllib2.Request(url = BASE_URI + uri_part, data = _data)
        request.add_header("Content-Type", "application/x-www-form-urlencoded")
    else:
        if not method:
            method = "GET"

        request = urllib2.Request(url = BASE_URI + uri_part)
    
    request.get_method = lambda: method        
    st = urllib2.urlopen(request)
    res = json.loads(st.read())
    print(res)
    cb(res)
    st.close()    


def test_register_channel():
    def _(res):
        assert(res["return_code"] > 0)
        assert(res["channel_id"] == "chan")
        
    _issue_command("/channels.json", { "channel_id": "chan" }, _)
    

def test_register_channel_with_sessions():
    def _(res):
        assert(res["return_code"] > 0)
        assert(res["channel_id"] == "chan-sess")
        
    _issue_command("/channels.json",
        { "channel_id": "chan-sess", "use_sessions": 1 }, _)
                
        
def test_push_content():
    def _(res):
        assert(res["return_code"] > 0)
        
    _issue_command("/channels/chan.json",
        { "content": "test" }, _)
        
        
def test_read_content():
    def _(res):
        assert(res["return_code"] > 0)
        assert(res["since"] == 0)
        
    _issue_command("/channels/chan.json", None, _)
    
    
def test_push_sess_content():
    def _(res):
        assert(res["return_code"] > 0)
        
    _issue_command("/channels/chan-sess.json",
        { "content": "test-sess" }, _)
        
        
def test_read_unbound_sess_content():
    def _(res):
        assert(res["return_code"] < 0)

    _issue_command("/channels/chan-sess.json?client_id=nonexistent", None, _)


def test_register_client_id():
    def _(res):
        assert(res["return_code"] > 0)
        assert(res["client_id"] == "cid")

    _issue_command("/clients.json", { "client_id": "cid" }, _)


def test_read_sess_content():
    def _(res):
        assert(res["return_code"] > 0)

    _issue_command("/channels/chan-sess.json?client_id=cid", None, _)


def test_delete_chan():
    def _(res):
        assert(res["return_code"] > 0)
        assert(res["removed"] == True)

    _issue_command("/channels/chan.json", None, _, "DELETE")
    _issue_command("/channels/chan-sess.json", None, _, "DELETE")    


def test_delete_nonexistent_chan():
    def _(res):
        assert(res["return_code"] > 0)
        assert(res["removed"] == False)        

    _issue_command("/channels/nonexistent.json", None, _, "DELETE")


    

        
        


    
