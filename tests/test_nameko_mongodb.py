import pytest
from mock import Mock
from nameko.testing.services import dummy
from nameko.containers import ServiceContainer
from pymongo import MongoClient

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
