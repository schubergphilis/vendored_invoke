import logging

from invoke import Collection

from . import template
from .configuration import INVOKE_LOGGING_LEVEL
from .utils import validate_log_level

logging.basicConfig(level=validate_log_level(INVOKE_LOGGING_LEVEL),
                    format='%(asctime)s %(name)s %(levelname)s %(message)s')

namespace = Collection()
namespace.add_task(template.create_requirements)
namespace.add_task(template.overwrite_from_remote_git)
namespace.add_task(template.update_libraries)
