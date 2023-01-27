from typing import Any


def load_ipython_extension(ip: Any) -> None:  # pragma: no cover
    # prevent circular import
    from _CI.vendor.rich.pretty import install
    from _CI.vendor.rich.traceback import install as tr_install

    install()
    tr_install()
