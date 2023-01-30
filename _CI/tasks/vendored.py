import logging

from invoke import task

from configuration import VENDORING_CLI, PIP_COMPILE_CLI, VENDOR_FILE
from helpers import clean_up, print_with_emoji

LOGGER = logging.getLogger(__name__)

@task
def update_libraries(context):
    """Updates the vendored dependencies by running the vendoring tool using vendor.txt requirements file."""
    arguments = ['sync', '.', '-v']
    command = f'{VENDORING_CLI} {" ".join(arguments)}'
    LOGGER.debug('Running command: %s', command)
    context.run(command)

@task
def clean_up_after_requirements_creation(context):
    """Called automatically by the create-requirements task."""
    temporary_dir_name = 'Test.egg-info'
    print(f'Removing temporary directory "{temporary_dir_name}" if exists.')
    # Platform independent way to delete files or directories
    success = clean_up(temporary_dir_name, logger=LOGGER)
    print_with_emoji('Done!', success=success)

@task(post=[clean_up_after_requirements_creation])
def create_requirements(context):
    """Creates the vendor.txt file by using pip-tools that would parse the vendor entry or pyproject.toml."""
    arguments = ['--extra=vendor', '--resolver=backtracking', '-o', str(VENDOR_FILE), 'pyproject.toml']
    command = f'{PIP_COMPILE_CLI} {" ".join(arguments)}'
    print('Please wait while pip-tools runs pip-compile on pyproject.toml to create the vendor file.')
    LOGGER.debug('Running command: %s', command)
    result = context.run(command, hide=True)
    exit_message = f'Successfully created {VENDOR_FILE}' if not result.exited else result.stderr
    print(exit_message)