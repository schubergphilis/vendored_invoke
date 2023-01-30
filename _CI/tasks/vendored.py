import logging

from invoke import task

from configuration import (VENDORING_CLI,
                           PIP_COMPILE_CLI,
                           VENDOR_FILE,
                           VENDOR_BIN_DIRECTORY)
from helpers import delete_file_or_directory, print_with_emoji

LOGGER = logging.getLogger(__name__)


@task
def generalise_python_shebang_in_bin(context):
    for file in VENDOR_BIN_DIRECTORY.glob('*'):
        with open(file, encoding='utf-8') as ifile:
            file_contents = ifile.readlines()
        file_contents[0] = '#!/usr/bin/env python\n'
        with open(file, 'w', encoding='utf-8') as ofile:
            ofile.writelines(file_contents)
    print_with_emoji(f'Successfully updated shebang in all files under bin directory.')


@task(post=[generalise_python_shebang_in_bin])
def update_libraries(context):
    """Updates the vendored dependencies by running the vendoring tool using vendor.txt requirements file."""
    arguments = ['sync', '.', '-v']
    command = f'{VENDORING_CLI} {" ".join(arguments)}'
    LOGGER.debug('Running command: %s', command)
    result = context.run(command)
    print_with_emoji(f'Vendored all libraries status: {"Success!" if result.ok else "Failed!"}', success=result.ok)

@task
def anonymize_pip_tools_command(context):
    text = open(VENDOR_FILE).read()
    start_marker = '--output-file='
    end_marker = '_CI/vendor.txt'
    text_to_remove = text[text.find(start_marker) + len(start_marker):text.find(end_marker)]
    text = text.replace(text_to_remove, '')
    VENDOR_FILE.write_text(text)
    print_with_emoji('Anonymized command written in vendor.txt', success=True)

@task(post=[anonymize_pip_tools_command])
def clean_up_after_requirements_creation(context):
    """Called automatically by the create-requirements task, no use as a stand alone command."""
    temporary_dir_name = 'Test.egg-info'
    print(f'Removing temporary directory "{temporary_dir_name}" if exists.')
    # Platform independent way to delete files or directories
    success = delete_file_or_directory(temporary_dir_name, logger=LOGGER)
    print_with_emoji('Done!', success=success)

@task(post=[clean_up_after_requirements_creation])
def create_requirements(context):
    """Creates the vendor.txt file by using pip-tools that would parse the vendor entry or pyproject.toml."""
    arguments = ['--extra=vendor', '--resolver=backtracking', '-o', str(VENDOR_FILE), 'pyproject.toml']
    command = f'{PIP_COMPILE_CLI} {" ".join(arguments)}'
    print('Please wait while pip-tools runs pip-compile on pyproject.toml to create the vendor file.')
    LOGGER.debug('Running command: %s', command)
    result = context.run(command, hide=True)
    exit_message = f'Successfully created {VENDOR_FILE}' if result.ok else result.stderr
    print_with_emoji(exit_message, success=result.ok)
