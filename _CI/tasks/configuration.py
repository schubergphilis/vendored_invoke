import os
from pathlib import Path

INVOKE_LOGGING_LEVEL = os.environ.get('INVOKE_LOGGING_LEVEL') or 'INFO'
CURRENT_SHELL = os.environ.get('SHELL', '').rpartition('/')[-1]

PROJECT_ROOT_DIRECTORY = Path(__file__).parent.parent.parent
CI_DIRECTORY = Path(PROJECT_ROOT_DIRECTORY, '_CI')
VENDOR_BIN_DIRECTORY = Path(CI_DIRECTORY, 'vendor', 'bin')
VENDORING_CLI = Path(VENDOR_BIN_DIRECTORY, 'vendoring')
PIP_COMPILE_CLI = Path(VENDOR_BIN_DIRECTORY, 'pip-compile')
VENDOR_FILE = Path(CI_DIRECTORY, 'vendor.txt')

EMOJI_SUCCESS_PREFIX = ':check_mark_button:'
EMOJI_SUCCESS_SUFFIX = ':thumbs_up:'
EMOJI_FAILURE_PREFIX = ':cross_mark:'
EMOJI_FAILURE_SUFFIX = ':crying_face:'