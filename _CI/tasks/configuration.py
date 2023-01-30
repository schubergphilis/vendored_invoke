from pathlib import Path

PROJECT_ROOT_DIRECTORY = Path(__file__).parent.parent.parent
CI_DIRECTORY = Path(PROJECT_ROOT_DIRECTORY, '_CI')
VENDOR_BIN = Path(CI_DIRECTORY, 'vendor', 'bin')
VENDORING_CLI = Path(VENDOR_BIN, 'vendoring')
PIP_COMPILE_CLI = Path(VENDOR_BIN, 'pip-compile')
VENDOR_FILE = Path(CI_DIRECTORY, 'vendor.txt')