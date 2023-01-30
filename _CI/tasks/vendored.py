import logging
from invoke import task
from configuration import VENDORING_CLI, PIP_COMPILE_CLI, VENDOR_FILE

LOGGER = logging.getLogger(__name__)

@task
def update_libraries(context):
    arguments = ['sync', '.', '-v']
    command = f'{VENDORING_CLI} {" ".join(arguments)}'
    LOGGER.debug('Running command: %s', command)
    context.run(command)

@task
def create_requirements(context):
    arguments = ['--extra=vendor', '--resolver=backtracking', '-o', str(VENDOR_FILE), 'pyproject.toml']
    command = f'{PIP_COMPILE_CLI} {" ".join(arguments)}'
    print('Please wait while pip-tools runs pip-compile on pyproject.toml to create the vendor file.')
    LOGGER.debug('Running command: %s', command)
    result = context.run(command, hide=True)
    exit_message = f'Succesfully created {VENDOR_FILE}' if not result.exited else result.stderr
    print(exit_message)