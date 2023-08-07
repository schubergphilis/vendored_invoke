import contextlib
import logging
import os
import shutil
import stat
import time
from pathlib import Path

import requests
from emoji import emojize
from rich.progress import Progress

from configuration import (EMOJI_SUCCESS_PREFIX,
                           EMOJI_SUCCESS_SUFFIX,
                           EMOJI_FAILURE_SUFFIX,
                           EMOJI_FAILURE_PREFIX)


def on_error(func, path, exc_info):  # pylint: disable=unused-argument
    """
    Error handler for ``shutil.rmtree``.

    If the error is due to an access error (read only file)
    it attempts to add write permission and then retries.

    If the error is for another reason it re-raises the error.

    Usage : ``shutil.rmtree(path, onerror=onerror)``

    # 2007/11/08
    # Version 0.2.6
    # pathutils.py
    # Functions useful for working with files and paths.
    # https://www.voidspace.org.uk/python/recipebook.shtml#utils

    # Copyright Michael Foord 2004
    # Released subject to the BSD License
    # Please see http://www.voidspace.org.uk/python/license.shtml

    # For information about bugfixes, updates and support, please join the Pythonutils mailing list.
    # http://groups.google.com/group/pythonutils/
    # Comments, suggestions and bug reports welcome.
    # Scripts maintained at http://www.voidspace.org.uk/python/index.shtml
    # E-mail fuzzyman@voidspace.org.uk
    """
    if not os.access(path, os.W_OK):
        # Is the error an access error ?
        os.chmod(path, stat.S_IWUSR)
        func(path)
    else:
        raise exc_info[1]


def delete_file_or_directory(items, logger):
    if not isinstance(items, (list, tuple)):
        items = [items]
    try:
        success = True
        for item in items:
            if os.path.isdir(item):
                logger.debug(f'Trying to remove directory "{item}"')
                shutil.rmtree(item, onerror=on_error)
            elif os.path.isfile(item):
                logger.debug(f'Trying to remove file "{item}"')
                os.unlink(item)
    except Exception:
        success = False
    return success


def emojize_message(message, success=True):
    """Prefixes and suffixes a message with emojis based on the flag provided for success.

    Args:
        message: The message.
        success: A boolean to flag the type of emoji used, possitive or negative.

    Returns:
        The embellished text.

    """
    success_emojis = (EMOJI_SUCCESS_PREFIX, EMOJI_SUCCESS_SUFFIX)
    failure_emojis = (EMOJI_FAILURE_PREFIX, EMOJI_FAILURE_SUFFIX)
    prefix, suffix = success_emojis if success else failure_emojis
    return f'{emojize(prefix)}  {message} {emojize(suffix)}'


def validate_log_level(level):
    """Validates a provided log level.

    Args:
        level: The level to validate.

    Returns:
        The logging level to use if the validation is correct, INFO otherwise.

    """
    levels = ('CRITICAL', 'ERROR', 'WARNING', 'INFO', 'DEBUG', 'NOTSET')
    level = level.upper()
    return getattr(logging, level) if level in levels else logging.INFO


@contextlib.contextmanager
def pushd(directory_name=None):
    """Temporarily changes the path to the provided one and reverts back automatically.

    Args:
        directory_name: The name of the directory to switch to.

    Returns:
        None

    """
    current_directory = os.getcwd()
    try:
        if directory_name is not None:
            os.chdir(directory_name)
        yield
    finally:
        os.chdir(current_directory)


def download_with_progress_bar(url, local_path='.', filename=None):
    """Downloads a file from a provided url showing a progress bar while doing it.

    Args:
        url: The url of the file.
        local_path: The local path to save the file to, defaults to local path.
        filename: A file name to use for the downloaded file if the remote needs to be overwritten.

    Returns:
        The full path of the downloaded file.

    """
    _, _, remote_filename = url.rpartition('/')
    filename = filename if filename else remote_filename
    with Progress() as progress:
        task = progress.add_task(f'[green]Downloading "{filename}"...', total=100)
        parent_path = Path(local_path)
        parent_path.mkdir(parents=True, exist_ok=True)
        full_path = parent_path / filename
        with requests.get(url, stream=True) as response, open(str(full_path), 'wb') as ofile:
            response.raise_for_status()
            total_size = int(response.headers.get("Content-Length"))
            chunk_size = 8192
            for chunk in response.iter_content(chunk_size=chunk_size):
                ofile.write(chunk)
                progress.update(task, advance=chunk_size / total_size * 100)
                time.sleep(.01)
            progress.stop_task(task)
    return str(full_path.resolve().absolute())
