import os
import stat
import shutil

from emoji import emojize
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
        raise

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

def print_with_emoji(message, success=True):
    prefix, suffix = (EMOJI_SUCCESS_PREFIX, EMOJI_SUCCESS_SUFFIX) if success \
        else (EMOJI_FAILURE_PREFIX, EMOJI_FAILURE_SUFFIX)
    print(f'{emojize(prefix)}  {message} {emojize(suffix)}')
