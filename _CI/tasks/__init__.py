import logging

from invoke import Collection

from _CI import (INVOKE_LOGGING_LEVEL,
                 validate_log_level)

logging.basicConfig(level=validate_log_level(INVOKE_LOGGING_LEVEL),
                    format='%(asctime)s %(name)s %(levelname)s %(message)s')

namespace = Collection()
