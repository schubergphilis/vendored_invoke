import logging
from invoke import task
LOGGER = logging.getLogger(__name__)

@task
def test(context):
    print('Test')