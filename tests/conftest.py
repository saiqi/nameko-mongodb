import eventlet
eventlet.monkey_patch()

from nameko.containers import ServiceContainer
import pytest


@pytest.yield_fixture
def container_factory():

    all_containers = []

    def make_container(service_cls, config, worker_ctx_cls=None):
        container = ServiceContainer(service_cls, config, worker_ctx_cls)
        all_containers.append(container)
        return container

    yield make_container

    for c in all_containers:
        try:
            c.stop()
        except:
            pass
