from __future__ import annotations

from _CI.vendor import click

from _CI.vendor.piptools.scripts import compile, sync


@click.group()
def cli() -> None:
    pass


cli.add_command(compile.cli, "compile")
cli.add_command(sync.cli, "sync")


# Enable ``python -m piptools ...``.
if __name__ == "__main__":  # pragma: no branch
    cli()
