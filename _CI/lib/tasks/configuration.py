import os
import tomllib
from pathlib import Path

INVOKE_LOGGING_LEVEL = os.environ.get('INVOKE_LOGGING_LEVEL') or 'INFO'
CURRENT_SHELL = os.environ.get('SHELL', '').rpartition('/')[-1] or 'windows'
CI_DIRECTORY_NAME = '_CI'
PROJECT_ROOT_DIRECTORY = next((directory for directory in Path(__file__).parents
                               if directory.name == CI_DIRECTORY_NAME)).parent

UPSTREAM_PROJECT_NAME = 'vendored_invoke'
PROJECT_NAME = PROJECT_ROOT_DIRECTORY.name
MAIN_BRANCH = 'main'

REMOTE_GIT_ZIP_DIR = f'https://codeload.github.com/schubergphilis/{UPSTREAM_PROJECT_NAME}/zip/refs/heads/{MAIN_BRANCH}'
REMOTE_ZIP_NAME = f'{UPSTREAM_PROJECT_NAME}-{MAIN_BRANCH}/'


CI_DIRECTORY = Path(PROJECT_ROOT_DIRECTORY, CI_DIRECTORY_NAME)
with open(CI_DIRECTORY / 'pyproject.toml', 'rb') as project_file:
    data = tomllib.load(project_file)
    TEMPLATE_NAME = data.get('project', {}).get('name')
    TEMPLATE_VERSION = data.get('project', {}).get('version')
    # Single source of truth for the maintenance tool pins: the `maintenance` extra above.
    # Bumping a version there changes the command actually run, with nothing to keep in step.
    MAINTENANCE_TOOLS = {
        requirement.partition('==')[0]: requirement
        for requirement in data.get('project', {}).get('optional-dependencies', {}).get('maintenance', [])
    }
LIB_DIRECTORY = Path(CI_DIRECTORY, 'lib')
TASKS_DIRECTORY = Path(LIB_DIRECTORY, 'tasks')

VENDOR_BIN_DIRECTORY = Path(LIB_DIRECTORY, 'vendor', 'bin')

# Run on demand through uv instead of from lib/vendor/bin. Vendoring the toolchain made
# re-vendoring self-hosting, but shipped ~5.8 MB of maintainer tooling to every consumer of
# the template. uv is the one prerequisite for maintaining this repository; consumers still
# need nothing but Python.
VENDORING_CLI = f'uvx --from {MAINTENANCE_TOOLS["vendoring"]} vendoring'
# uv resolves the extra natively, so pip-tools is not needed at all. It also writes the
# command into the header using the relative path it was given, which is why there is no
# longer an "anonymize" step stripping a local absolute path out of vendor.txt.
PIP_COMPILE_CLI = 'uv pip compile'

VENDOR_FILE = Path(LIB_DIRECTORY, 'vendor.txt')
PYPROJECT_FILE = Path(CI_DIRECTORY, 'pyproject.toml')
WORKFLOW_SCRIPT_FILE = Path(CI_DIRECTORY, 'template-workflow')

BACKBONE_STRUCTURE = [str(LIB_DIRECTORY),
                      str(Path(CI_DIRECTORY / '__init__.py')),
                      str(PYPROJECT_FILE),
                      str(WORKFLOW_SCRIPT_FILE)]

# Literal characters rather than `:shortcode:` strings. These were the only reason the `emoji`
# package was vendored — 4.2 MB of Unicode data tables, in every consumer, to turn four
# constants into four characters.
EMOJI_SUCCESS_PREFIX = '✅'
EMOJI_SUCCESS_SUFFIX = '👍'
EMOJI_FAILURE_PREFIX = '❌'
EMOJI_FAILURE_SUFFIX = '😢'
