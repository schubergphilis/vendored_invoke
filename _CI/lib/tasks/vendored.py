import logging

from invoke import task

from configuration import (VENDORING_CLI,
                           PIP_COMPILE_CLI,
                           PYPROJECT_FILE,
                           TEMPLATE_NAME,
                           VENDOR_FILE,
                           VENDOR_BIN_DIRECTORY)
from helpers import delete_file_or_directory, emojize_message, pushd

LOGGER = logging.getLogger(__name__)


@task
def generalise_python_shebang_in_bin(context):
    for file in VENDOR_BIN_DIRECTORY.glob('*'):
        with open(file, encoding='utf-8') as ifile:
            file_contents = ifile.readlines()
        file_contents[0] = '#!/usr/bin/env python\n'
        with open(file, 'w', encoding='utf-8') as ofile:
            ofile.writelines(file_contents)
    LOGGER.info(emojize_message(f'Successfully updated shebang in all files under bin directory.'))


@task(post=[generalise_python_shebang_in_bin])
def update_libraries(context):
    """Updates the vendored dependencies by running the vendoring tool using vendor.txt requirements file."""
    arguments = ['sync', '.', '-v']
    command = f'{VENDORING_CLI} {" ".join(arguments)}'
    LOGGER.debug('Running command: %s', command)
    result = context.run(command)
    message = emojize_message(f'Vendored all libraries status: {"Success!" if result.ok else "Failed!"}',
                              success=result.ok)
    LOGGER.info(message)


@task
def anonymize_pip_tools_command(context):
    text = open(VENDOR_FILE).read()
    start_marker = '--output-file='
    end_marker = 'lib/vendor.txt'
    text_to_remove = text[text.find(start_marker) + len(start_marker):text.find(end_marker)]
    text = text.replace(text_to_remove, '')
    VENDOR_FILE.write_text(text)
    LOGGER.info(emojize_message('Anonymized command written in vendor.txt', success=True))


@task(post=[anonymize_pip_tools_command])
def clean_up_after_requirements_creation(context):
    """Called automatically by the create-requirements task, no use as a standalone command."""
    temporary_dir_name = f'{TEMPLATE_NAME}.egg-info'
    LOGGER.info(f'Removing temporary directory "{temporary_dir_name}" if exists.')
    # Platform independent way to delete files or directories
    success = delete_file_or_directory(temporary_dir_name, logger=LOGGER)
    LOGGER.info(emojize_message('Done!', success=success))


@task(post=[clean_up_after_requirements_creation])
def create_requirements(context):
    """Creates the vendor.txt file by using pip-tools that would parse the vendor entry or pyproject.toml."""
    arguments = ['--extra=vendor', '--resolver=backtracking', '-o', str(VENDOR_FILE), str(PYPROJECT_FILE), '--verbose']
    command = f'{PIP_COMPILE_CLI} {" ".join(arguments)}'
    LOGGER.info('Please wait while pip-tools runs pip-compile on pyproject.toml to create the vendor file.')
    LOGGER.debug('Running command: %s', command)
    result = context.run(command, hide=True)
    exit_message = f'Successfully created {VENDOR_FILE}' if result.ok else result.stderr
    LOGGER.info(emojize_message(exit_message, success=result.ok))