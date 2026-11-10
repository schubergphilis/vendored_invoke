# vendored_invoke

A portable [invoke](https://www.pyinvoke.org/) you can drop into any repository to build a
development workflow. Consumers need one thing: [uv](https://docs.astral.sh/uv/). Not even
Python, because uv provides it. There is no virtualenv to manage, no `pip install` and no
lockfile. `_CI/lib/vendor/` holds the libraries, and `workflow.cmd` runs them.

Maintaining this repository needs uv and a Python 3.11+ on `PATH`.

## What is in the vendored tree, and why

Everything in `_CI/lib/vendor/` is copied into every repository that adopts this template, so
the bar for adding something is high: **the shipped code under `_CI/` must import it.**

| Package | Why |
| --- | --- |
| `invoke` | The task runner. The whole point. |

That is 55 files and ~545 KiB, all pure Python.

Three things are deliberately **not** vendored:

- **The vendoring toolchain** (`vendoring`, `pip-tools`). It used to be, which made re-vendoring
  self-hosting — but it also shipped ~5.8 MB of maintainer tooling, plus `rich`, `requests`,
  `jsonschema`, `pygments`, `urllib3` and friends, to every consumer. It is now run on demand
  with `uvx`.
- **`tomli`.** `configuration.py` parses TOML, but `tomli` only publishes mypyc-compiled
  wheels, so vendoring it produced a `__mypyc.cpython-314-darwin.so` — a 427 KiB binary tied to
  one OS, architecture and Python version, in a tree whose purpose is running anywhere. stdlib
  `tomllib` does the same job for free, which is why `requires-python` is `>=3.11`.
- **`coloredlogs`.** It only coloured the log output, and it brought `humanfriendly` with it.
  The tasks configure stdlib `logging` instead.

## Re-vendoring from scratch

Four steps. Run them from `_CI/`, except where noted. `./template-workflow update-libraries`,
run from `_CI/`, does steps 2–4 in one go; the steps are spelled out here so each one can be
checked by hand.

### 1. Declare what you want

`_CI/pyproject.toml` has two extras, and the distinction matters:

```toml
[project.optional-dependencies]
vendor      = ['invoke']                  # content — ends up in lib/vendor/
maintenance = ['vendoring==1.2.0']        # tooling — runs the vendoring, never vendored
```

Anything you add to `vendor` is resolved *with its full dependency tree* and copied in. Adding
one convenience library can pull a dozen packages; check what you are signing up for before
committing the result.

### 2. Resolve the dependency tree

```bash
uv pip compile --extra=vendor -o lib/vendor.txt pyproject.toml
```

This replaces `pip-compile`. It writes the exact command into the file header using the
relative path you gave it, so there is no absolute path to strip afterwards.

### 3. Sync the tree

```bash
uvx --from vendoring==1.2.0 --with pip vendoring sync .
```

`--with pip` is required: `vendoring` shells out to `pip` to download, and a `uvx` tool
environment has no `pip` of its own.

This clears `lib/vendor/`, downloads everything in `lib/vendor.txt`, rewrites absolute imports
into the `lib.vendor` namespace, applies `drop` rules and `lib/patches/`, and generates `.pyi`
stubs. Configuration lives in `[tool.vendoring]` in `_CI/pyproject.toml`.

### 4. Generalise the shebangs

```bash
python - <<'PY'
import pathlib
for script in sorted(pathlib.Path('lib/vendor/bin').iterdir()):
    lines = script.read_text(encoding='utf-8').splitlines(keepends=True)
    lines[0] = '#!/usr/bin/env python\n'
    script.write_text(''.join(lines), encoding='utf-8')
    script.chmod(0o755)
PY
```

pip writes the absolute path of whatever interpreter did the install into each console script.
Left alone, the committed tree only runs on the machine that generated it.

Then verify before committing:

```bash
python lib/vendor/bin/invoke --version
git diff --stat            # from the repository root
```

## Patches

`vendoring` applies everything in `lib/patches/` during step 3. These are the only
hand-maintained pieces of the tree.

### `vendored_version.patch`

invoke 3.x reads its own version from installed package metadata
(`importlib.metadata.version("invoke")`). A vendored copy is not an installed distribution,
so the lookup raises `PackageNotFoundError` on import and nothing runs. The patch replaces the
lookup with a hard-coded string.

When you upgrade invoke, update the version string in the patch to match `lib/vendor.txt`.
If upstream only bumps its version, the patch still applies cleanly, and `--version` reports
the old number without any error.

### `path_inject.patch`

It inserts a `sys.path`
prelude into `lib/vendor/bin/inv` and `lib/vendor/bin/invoke` so the launcher can import both
the vendored libraries and the consuming project's `_CI` package without anything installed.

Two constraints if you ever regenerate it:

- **Every surviving script in `bin/` needs a hunk.** A hunk for a script that no longer exists
  makes `vendoring sync` fail outright. This is why unused console entry points are listed
  under `drop` rather than left in place.
- **Keep the shebang out of the diff context.** Line 1 holds a machine-specific interpreter
  path, so a patch generated with the default three lines of context only applies on the
  machine that made it. Generate it with one line of context.

To regenerate: move the patch aside, run step 3 to get unpatched scripts, insert the prelude,
then diff the before and after with `-U1`, writing hunks with `a/` and `b/` prefixes relative
to the repository root.

## Adding a library

1. Add it to the `vendor` extra.
2. Run steps 2–4.
3. Check the diff. If the tree grew far more than the library itself, its dependencies came
   too — decide whether that is acceptable before committing.
4. If `vendoring sync` leaves a module importing a bare top-level name, add a rule to
   `[tool.vendoring.transformations].substitute`. The list is empty on purpose; every rule it
   used to hold existed to prop up the accidentally-vendored toolchain.
5. If the library ships a console script you never run, add it to `drop` — each one otherwise
   needs its own patch hunk.

## Consuming this template

Copy `_CI/` and `workflow.cmd` into your repository and define tasks under `_CI/tasks/`. Run
them from the repository root:

```bash
./workflow.cmd <task>     # macOS, Linux, any POSIX sh
workflow.cmd <task>       # Windows, from cmd or PowerShell
./workflow.cmd            # no arguments: same as --list
```

`workflow.cmd` is one file that is valid as both a POSIX shell script and a Windows batch
file. `sh` treats line 1 as a no-op `:` followed by the real command, and `exec` means it
never reads further. `cmd` treats line 1 as a label and skips it, then runs the rest under
`setlocal`, so nothing it sets leaks into the calling shell. Both sides clear `VIRTUAL_ENV`
so an activated virtualenv from elsewhere does not leak in, substitute `--list` when given no
arguments, then start invoke through `uv run`.

If your repository has its own `pyproject.toml`, `uv run` syncs that project's environment
before starting invoke, so tasks can import your project's dependencies.
