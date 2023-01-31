"""
A performance benchmark using the example from issue #232.

See https://github.com/python-jsonschema/jsonschema/pull/232.
"""
from pathlib import Path

from pyperf import Runner
from _CI.vendor.pyrsistent import m

from _CI.vendor.jsonschema.tests._suite import Version
from _CI.vendor import jsonschema

issue232 = Version(
    path=Path(__file__).parent / "issue232",
    remotes=m(),
    name="issue232",
)


if __name__ == "__main__":
    issue232.benchmark(
        runner=Runner(),
        Validator=jsonschema.Draft4Validator,
    )