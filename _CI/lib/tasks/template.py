import logging
import shutil
import zipfile
from itertools import chain
from pathlib import Path
from tempfile import TemporaryDirectory

from invoke import task

from .configuration import (BACKBONE_STRUCTURE,
                            CI_DIRECTORY,
                            ENTRYPOINT_SCRIPT_FILE,
                            PIP_COMPILE_CLI,
                            PROJECT_ROOT_DIRECTORY,
                            PYPROJECT_FILE,
                            REMOTE_GIT_ZIP_DIR,
                            REMOTE_ZIP_NAME,
                            VENDOR_FILE,
                            VENDOR_BIN_DIRECTORY,
                            VENDORING_CLI,
                            WORKFLOW_SCRIPT_FILE)
from .utils import (delete_file_or_directory,
                    emojize_message,
                    pushd,
                    download_with_progress_bar,
                    make_file_executable)

LOGGER = logging.getLogger(__name__)


@task
def create_requirements(context):
    """Creates the vendor.txt file by resolving the vendor extra of pyproject.toml with uv."""
    # Relative paths, run from _CI/: uv writes the command verbatim into the vendor.txt header, so
    # absolute paths would leak the local checkout location into the committed file.
    arguments = ['--extra=vendor',
                 '-o', str(VENDOR_FILE.relative_to(CI_DIRECTORY)),
                 str(PYPROJECT_FILE.relative_to(CI_DIRECTORY)),
                 '--verbose']
    command = f'{PIP_COMPILE_CLI} {" ".join(arguments)}'
    LOGGER.info('Please wait while uv resolves the vendor extra of pyproject.toml into the vendor file.')
    LOGGER.debug(f'Running command: {command}')
    with context.cd(CI_DIRECTORY):
        result = context.run(command, hide=True)
    exit_message = f'Successfully created {VENDOR_FILE}' if result.ok else result.stderr
    LOGGER.info(emojize_message(exit_message, success=result.ok))


@task
def generalise_python_shebang_in_bin(context):
    for file in VENDOR_BIN_DIRECTORY.glob('*'):
        try:
            with open(file, encoding='utf-8') as ifile:
                file_contents = ifile.readlines()
            file_contents[0] = '#!/usr/bin/env python\n'
            with open(file, 'w', encoding='utf-8') as ofile:
                ofile.writelines(file_contents)
            LOGGER.debug(f'Successfully updated shebang for file "{file}"')
        except UnicodeDecodeError:
            LOGGER.warning(f'File "{file}" does not seem to be a text file, cannot update the shebang.')
    LOGGER.info(emojize_message('Successfully updated shebang in all files under bin directory.'))


@task(pre=[create_requirements], post=[generalise_python_shebang_in_bin])
def update_libraries(context):
    """Updates the vendored dependencies by running the vendoring tool using vendor.txt requirements file."""
    arguments = ['sync', '.', '-v']
    command = f'{VENDORING_CLI} {" ".join(arguments)}'
    LOGGER.debug(f'Running command: {command}')
    # vendoring reads [tool.vendoring] from the pyproject.toml in the directory it is given.
    with context.cd(CI_DIRECTORY):
        result = context.run(command)
    message = emojize_message(f'Vendored all libraries status: {"Success!" if result.ok else "Failed!"}',
                              success=result.ok)
    LOGGER.info(message)


@task
def overwrite_from_remote_git(context):
    """Overwrites all remote existing files.

    Downloads the remote main branch as zip and overwrites all appropriate files of the _CI/ structure.

    """
    with TemporaryDirectory() as temp_dir, pushd(temp_dir):
        backbone_zip_path = download_with_progress_bar(REMOTE_GIT_ZIP_DIR, local_path=temp_dir)
        LOGGER.debug(f'Zip file path is {backbone_zip_path}')
        with zipfile.ZipFile(backbone_zip_path) as backbone_zip:
            backbone_zip.extractall()
        LOGGER.debug('Extracted all contents of the downloaded zip.')
        with pushd(REMOTE_ZIP_NAME):
            delete_file_or_directory(BACKBONE_STRUCTURE)
            LOGGER.debug(f'Copying tree of {Path(REMOTE_ZIP_NAME).resolve()} '
                         f'over {PROJECT_ROOT_DIRECTORY}')
            shutil.copytree('.', PROJECT_ROOT_DIRECTORY, dirs_exist_ok=True)
    # ZipFile.extractall does not restore permission bits, so every script loses its executable flag.
    for filename in chain([WORKFLOW_SCRIPT_FILE, ENTRYPOINT_SCRIPT_FILE], VENDOR_BIN_DIRECTORY.iterdir()):
        make_file_executable(filename.resolve())
    LOGGER.info(emojize_message('Successfully overwrote the _CI directory with remote contents where possible',
                                success=True))
