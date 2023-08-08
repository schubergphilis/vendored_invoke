import os
from pathlib import Path

import tomli

PROJECT_NAME = 'vendored_invoke'
MAIN_BRANCH = 'main'

REMOTE_GIT_ZIP_DIR = f'https://github.com/schubergphilis/{PROJECT_NAME}/archive/refs/heads/{MAIN_BRANCH}.zip'
REMOTE_ZIP_NAME = f'{PROJECT_NAME}-{MAIN_BRANCH}/'


WORKFLOW_SCRIPT_NAME = 'template-workflow'

INVOKE_LOGGING_LEVEL = os.environ.get('INVOKE_LOGGING_LEVEL') or 'INFO'
CURRENT_SHELL = os.environ.get('SHELL', '').rpartition('/')[-1] or 'windows'
CI_DIRECTORY_NAME = '_CI'
PROJECT_ROOT_DIRECTORY = next((directory for directory in Path(__file__).parents
                               if directory.name == CI_DIRECTORY_NAME)).parent
CI_DIRECTORY = Path(PROJECT_ROOT_DIRECTORY, CI_DIRECTORY_NAME)
with open(CI_DIRECTORY / 'pyproject.toml', 'rb') as project_file:
    data = tomli.load(project_file)
    TEMPLATE_NAME = data.get('project', {}).get('name')
    TEMPLATE_VERSION = data.get('project', {}).get('version')
LIB_DIRECTORY = Path(CI_DIRECTORY, 'lib')

VENDOR_BIN_DIRECTORY = Path(LIB_DIRECTORY, 'vendor', 'bin')

VENDORING_CLI = Path(VENDOR_BIN_DIRECTORY, 'vendoring')
PIP_COMPILE_CLI = Path(VENDOR_BIN_DIRECTORY, 'pip-compile')

VENDOR_FILE = Path(LIB_DIRECTORY, 'vendor.txt')
PYPROJECT_FILE = Path(CI_DIRECTORY, 'pyproject.toml')

EMOJI_SUCCESS_PREFIX = ':check_mark_button:'
EMOJI_SUCCESS_SUFFIX = ':thumbs_up:'
EMOJI_FAILURE_PREFIX = ':cross_mark:'
EMOJI_FAILURE_SUFFIX = ':crying_face:'
