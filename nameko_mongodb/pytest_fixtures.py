import pytest

from pymongo import MongoClient


@pytest.fixture(scope='session')
def url(request):
    return request.config.getoption('TEST_DB_URL')


@pytest.fixture(scope='session')
def database(url):
    client = MongoClient(url)
    db = client['test_db']

    yield db

    client.drop_database(db)
    client.close()

