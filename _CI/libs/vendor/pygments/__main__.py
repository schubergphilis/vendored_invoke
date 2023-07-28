"""
    pygments.__main__
    ~~~~~~~~~~~~~~~~~

    Main entry point for ``python -m pygments``.

    :copyright: Copyright 2006-2023 by the Pygments team, see AUTHORS.
    :license: BSD, see LICENSE for details.
"""

import sys
import libs.vendor.pygments.cmdline

try:
    sys.exit(pygments.cmdline.main(sys.argv))
except KeyboardInterrupt:
    sys.exit(1)
