import logging

from invoke import task

LOGGER = logging.getLogger(__name__)


@task
def print_shell(context):
    # result = context.run('echo $0')
    # print(result.stdout, result.stderr)
    print(1)

@task
def print_shell2(context):
    # result = context.run('echo $0')
    # print(result.stdout, result.stderr)
    print(2)