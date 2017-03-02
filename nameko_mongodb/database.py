from weakref import WeakKeyDictionary
import datetime

from pymongo import MongoClient
from nameko.extensions import DependencyProvider


class MongoDatabase(DependencyProvider):

    def __init__(self, result_backend=True):
        self.result_backend = result_backend
        self.logs = WeakKeyDictionary()
        
    def setup(self):
        conn_uri = self.container.config['MONGODB_CONNECTION_URL']

        self.client = MongoClient(conn_uri)

        self.database = self.client[self.container.service_name]

        if 'MONGODB_USER' in self.container.config and self.container.config['MONGODB_USER'] != "":
            self.database.authenticate(self.container.config['MONGODB_USER'],
                                       self.container.config['MONGODB_PASSWORD'],
                                       source=self.container.config['MONGODB_AUTHENTICATION_BASE'])

        self.database['_logging'].create_index('call_id')

    def stop(self):
        self.client.close()
        del self.client

    def get_dependency(self, worker_ctx):
        return self.database
    
    def worker_setup(self, worker_ctx):
        if self.result_backend:
            self.logs[worker_ctx] = datetime.datetime.now()

            service_name = worker_ctx.service_name
            method_name = worker_ctx.entrypoint.method_name
            call_id = worker_ctx.call_id

            self.database['logging'].insert_one(
                {
                    'call_id': call_id,
                    'service_name': service_name,
                    'method_name': method_name,
                    'status': 'PENDING',
                    'start': self.logs[worker_ctx]
                }
            )

    def worker_result(self, worker_ctx, result=None, exc_info=None):
        if self.result_backend:
            call_id = worker_ctx.call_id

            if exc_info is None:
                status = 'SUCCESS'
            else:
                status = 'FAILED'

            now = datetime.datetime.now()

            start = self.logs.pop(worker_ctx)

            self.database['_logging'].update_one(
                {'call_id': call_id},
                {
                    '$set': {
                        'status': status,
                        'end': now,
                        'elapsed': (now - start).seconds
                    }
                }
            )
