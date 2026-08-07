import contextlib
import logging
import os
import shutil
import stat
import sys
import urllib.request
from pathlib import Path

from .configuration import (EMOJI_SUCCESS_PREFIX,
                            EMOJI_SUCCESS_SUFFIX,
                            EMOJI_FAILURE_SUFFIX,
                            EMOJI_FAILURE_PREFIX,
                            VENDOR_BIN_DIRECTORY)

LOGGER = logging.getLogger(__name__)


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


def delete_file_or_directory(items):
    if not isinstance(items, (list, tuple)):
        items = [items]
    try:
        success = True
        for item in items:
            if os.path.isdir(item):
                LOGGER.debug(f'Trying to remove directory "{item}"')
                shutil.rmtree(item, onerror=on_error)
            elif os.path.isfile(item):
                LOGGER.debug(f'Trying to remove file "{item}"')
                os.unlink(item)
    except Exception:
        LOGGER.exception('Failed deleting something...')
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
    return f'{prefix}  {message} {suffix}'


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
            LOGGER.debug(f'Changing over to directory {directory_name}')
            os.chdir(directory_name)
        yield
    finally:
        LOGGER.debug(f'Changing over to directory {current_directory}')
        os.chdir(current_directory)


def _report_progress(filename, written, total_length):
    """Write a single-line progress indicator to stderr, or nothing when not a terminal.

    Deliberately plain: a rich progress bar cost 1.1 MB of vendored `rich` plus its
    markdown-it, pygments and mdurl dependencies, in every project built on this template.
    """
    if not sys.stderr.isatty():
        return
    if total_length:
        sys.stderr.write(f'\rDownloading "{filename}"... {written / total_length:.0%}')
    else:
        sys.stderr.write(f'\rDownloading "{filename}"... {written // 1024} KiB')
    sys.stderr.flush()


def download_with_progress_bar(url, local_path='.', filename=None):
    """Downloads a file from a provided url showing progress while doing it.

    Uses `urllib` from the standard library, so downloading needs nothing vendored.

    Args:
        url: The url of the file.
        local_path: The local path to save the file to, defaults to local path.
        filename: A file name to use for the downloaded file if the remote needs to be overwritten.

    Returns:
        The full path of the downloaded file.

    """
    chunk_size = 8192
    _, _, remote_filename = url.rpartition('/')
    filename = filename if filename else remote_filename
    parent_path = Path(local_path)
    parent_path.mkdir(parents=True, exist_ok=True)
    full_path = parent_path / filename
    # Only http(s) is ever passed here (see REMOTE_GIT_ZIP_DIR); reject anything else rather
    # than let urlopen handle a file:// or data: URL.
    if not url.lower().startswith(('http://', 'https://')):
        raise ValueError(f'Refusing to download from a non-http(s) url: {url}')
    written = 0
    with urllib.request.urlopen(url) as response:  # noqa: S310
        content_length = response.headers.get('Content-Length')
        total_length = int(content_length) if content_length else 0
        if not total_length:
            LOGGER.info('Transfer encoding detected, actual size is unknown, cannot display an accurate percentage.')
        with open(str(full_path), 'wb') as ofile:
            while chunk := response.read(chunk_size):
                ofile.write(chunk)
                written += len(chunk)
                _report_progress(filename, written, total_length)
    if sys.stderr.isatty():
        sys.stderr.write('\n')
    return str(full_path.resolve())


def make_file_executable(filename):
    os.chmod(filename, os.stat(filename).st_mode | stat.S_IEXEC)
    LOGGER.debug(f'Made {filename} executable.')


def get_binary_path(executable):
    """Gets the software name and returns the path of the binary."""
    if (bin_path := str(VENDOR_BIN_DIRECTORY.resolve())) not in os.environ.get('PATH'):
        LOGGER.debug(f'Adding path {bin_path} to environment PATH variable')
        os.environ['PATH'] = os.pathsep.join([bin_path, os.environ['PATH']])
    if all([executable == 'start',
            sys.platform == 'win32']):
        return executable
    return shutil.which(executable)
