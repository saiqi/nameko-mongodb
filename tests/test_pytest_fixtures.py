from pymongo.collection import Collection
from nameko_mongodb.pytest_fixtures import database, url


def test_can_create_collection(database):
    collection = database['test_collection']
    assert isinstance(collection, Collection)


def test_database_can_insert_doc(database):
    result = database.collection.insert_one({'toto': 'titi'})
    assert result.inserted_id is not None
