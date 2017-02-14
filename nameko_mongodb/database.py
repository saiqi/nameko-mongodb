from weakref import WeakKeyDictionary

from pymongo import MongoClient
from nameko.extensions import DependencyProvider


class MongoDatabase(DependencyProvider):
    
    def __init__(self):
        self.client = None
        self.databases = WeakKeyDictionary()
        
    def setup(self):
        conn_uri = self.container.config['MONGODB_CONNECTION_URL']

        self.client = MongoClient(conn_uri)

    def stop(self):
        self.client.close()
        del self.client


    def get_dependency(self, worker_ctx):
        _db = self.client[self.container.service_name]

        if 'MONGODB_USER' in self.container.config and self.container.config['MONGODB_USER'] != "":
            _db.authenticate(self.container.config['MONGODB_USER'],
                                       self.container.config['MONGODB_PASSWORD'],
                                       source=self.container.config['MONGODB_AUTHENTICATION_BASE'])
                                       
        return _db
        