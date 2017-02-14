from weakref import WeakKeyDictionary
import pytest
from mock import Mock
from nameko.testing.services import dummy, entrypoint_hook
from nameko.containers import ServiceContainer, WorkerContext
from pymongo import MongoClient
from pymongo.database import Database

from nameko_mongodb.database import MongoDatabase 

class DummyService(object):
    name = 'dummy_service'
    
    database = MongoDatabase()
    
    @dummy
    def insert_one(self, document):
        res = self.database.test_collection.insert_one(document)
        return res
        
    @dummy
    def find_one(self, query):
        doc = self.database.test_collection.find_one(query)
        return doc
        

@pytest.fixture
def config():
    return {
        'MONGODB_CONNECTION_URL':'mongodb://mongodb:27017'
    }
    
@pytest.fixture
def container(config):
    return Mock(spec=ServiceContainer, config=config, service_name='dummy_service')
    
@pytest.fixture
def database(container):
    return MongoDatabase().bind(container, 'database')
    
def test_setup(database):
    database.setup()
    assert isinstance(database.client, MongoClient)

def test_stop(database):
    database.setup()
    assert database.client
    
    database.stop()
    assert not hasattr(database, 'client')
    
def test_get_dependency(database):
    database.setup()
    
    worker_ctx = Mock(spec=WorkerContext)
    db = database.get_dependency(worker_ctx)
    assert isinstance(db, Database)
    assert database.databases[worker_ctx] is db
    
def test_multiple_workers(database):
    database.setup()
    
    worker_ctx_1 = Mock(spec=WorkerContext)
    db_1 = database.get_dependency(worker_ctx_1)
    assert isinstance(db_1, Database)
    assert database.databases[worker_ctx_1] is db_1
    
    worker_ctx_2 = Mock(spec=WorkerContext)
    db_2 = database.get_dependency(worker_ctx_2)
    assert isinstance(db_2, Database)
    assert database.databases[worker_ctx_2] is db_2
    
    assert database.databases == WeakKeyDictionary({
        worker_ctx_1: db_1,
        worker_ctx_2: db_2
    })
    
def test_weakref(database):
    database.setup()
    
    worker_ctx = Mock(spec=WorkerContext)
    db = database.get_dependency(worker_ctx)
    assert isinstance(db, Database)
    assert database.databases[worker_ctx] is db
    
    database.worker_teardown(worker_ctx)
    assert worker_ctx not in database.databases
    
def test_end_to_end(container_factory):

    config = {
        'MONGODB_CONNECTION_URL': 'mongodb://mongodb:27017'
    }
    
    container = container_factory(DummyService, config)
    container.start()
    
    with entrypoint_hook(container, 'insert_one') as insert_one:
        res = insert_one({'toto':'titi'})
        
    with entrypoint_hook(container, 'find_one') as find_one:
        doc = find_one({'toto':'titi'})
        assert doc['toto'] == 'titi'
    
    