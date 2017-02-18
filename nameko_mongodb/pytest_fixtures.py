import pytest

from pymongo import MongoClient


def pytest_adoption(parser):
    parser.adoption(
        '--test-db-url',
        action='store',
        dest='TEST_DB_URL',
        default='mongodb://localhost:27017',
        help=(
            'DB url for testing (e.g. mongodb://mongodb:27017)'
        )
    )


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

