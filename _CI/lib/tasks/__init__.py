import coloredlogs
from invoke import Collection

import vendored
from configuration import INVOKE_LOGGING_LEVEL
from helpers import validate_log_level

coloredlogs.install(level=validate_log_level(INVOKE_LOGGING_LEVEL))

namespace = Collection()
namespace.add_collection(vendored)
