
from nose.tools import *
from simple_comet import main
import os
import signal

server_pid = 0

def setup():
	server_pid = os.fork()
	if server_pid == 0:
		main()
		exit(0)

		
def teardown():
	os.kill(server_pid, signal.SIGTERM)
	pass

	
def test_basic():
	pass

