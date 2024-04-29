import pytest
import cProfile
import logging
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import client
import worker
from log import setup_logging



# Set up logging path
setup_logging()

# Create a logger
logger = logging.getLogger(__name__)

def test_worker():
    w = worker.Worker()
    worker.start_worker(w, True)
    assert w.alive == True

    worker.exit_worker(w)
    assert w.alive == False
    pass


def test_client_success():
    w = worker.Worker()
    assert w.alive == True

    c = client.Client("client 1", "localhost", 8000)
    
    assert c.username == "client 1"
    assert c.uuid == client.hashFunction("client 1")
    assert c.online == True
    assert c.myaddr == ("127.0.0.1", 8000)
    pass



def test_client_ping():
    pass

def test_client_messaging():
    pass

def test_worker_discovery():
    pass