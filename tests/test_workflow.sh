#!/bin/sh
# Smoke-test workflow.cmd against every supported Python version.
#
# Usage: tests/test_workflow.sh [version ...]     (default: 3.11 3.12 3.13 3.14 3.15)
#
# For each version the test checks that:
#   - `workflow.cmd` with no arguments prints the same output as `workflow.cmd --list`
#   - neither prints a traceback
#   - `workflow.cmd --help` succeeds with stdout on a pseudo-terminal. invoke only queries the
#     terminal size on a TTY, which is where Python 3.14 raised `SystemError: buffer overflow`
#     against invoke 2.2.0, so a plain pipe would not catch that regression.

set -u

cd "$(dirname "$0")/.." || exit 2
[ $# -gt 0 ] || set -- 3.11 3.12 3.13 3.14 3.15

# Use only interpreters uv manages, downloading any that are missing. Without this, uv also
# probes every `python` on PATH, and a wrapper there that itself calls `uv run python` makes
# uv recurse forever for any version it has no managed install of.
export UV_PYTHON_PREFERENCE=only-managed

# Runs workflow.cmd through `sh`: line 1 is the `: ;` polyglot trick, not a shebang, so
# exec() rejects the file with ENOEXEC. Prints combined output and exits with the command's
# status, or 124 on timeout. With `tty`, stdout and stderr are a pseudo-terminal.
RUNNER='
import os, subprocess, sys
tty, args = sys.argv[1] == "tty", ["sh", "./workflow.cmd", *sys.argv[2:]]
if not tty:
    try:
        done = subprocess.run(args, stdin=subprocess.DEVNULL, stdout=subprocess.PIPE,
                              stderr=subprocess.STDOUT, timeout=300)
    except subprocess.TimeoutExpired:
        sys.exit(124)
    sys.stdout.buffer.write(done.stdout)
    sys.exit(done.returncode)
leader, follower = os.openpty()
child = subprocess.Popen(args, stdin=subprocess.DEVNULL, stdout=follower, stderr=follower)
os.close(follower)
output = b""
while True:
    try:
        chunk = os.read(leader, 4096)
    except OSError:  # EIO once the child closes its end
        break
    if not chunk:
        break
    output += chunk
try:
    status = child.wait(timeout=300)
except subprocess.TimeoutExpired:
    child.kill()
    status = 124
sys.stdout.buffer.write(output.replace(b"\r\n", b"\n"))
sys.exit(status)
'

failures=0

fail() {
    echo "  FAIL: $1"
    failures=$((failures + 1))
}

for version in "$@"; do
    echo "== Python $version"
    export UV_PYTHON="$version"

    if ! actual=$(uv --quiet run python -c 'import platform; print(platform.python_version())' 2>&1); then
        fail "uv could not provide Python $version: $actual"
        continue
    fi
    echo "  interpreter: $actual"

    no_args=$(uv run python -c "$RUNNER" pipe 2>&1)
    list=$(uv run python -c "$RUNNER" pipe --list 2>&1)

    case "$no_args$list" in
        *Traceback*) fail "traceback in task listing:
$no_args
$list" ;;
    esac
    [ "$no_args" = "$list" ] || fail "no-argument output differs from --list:
--- no arguments
$no_args
--- --list
$list"

    help=$(uv run python -c "$RUNNER" tty --help 2>&1)
    status=$?
    case "$help" in
        *Traceback*) fail "traceback in --help on a TTY:
$help" ;;
        *"Core options:"*) [ "$status" -eq 0 ] || fail "--help on a TTY exited $status" ;;
        *) fail "--help on a TTY printed no help (exit $status):
$help" ;;
    esac
done

if [ "$failures" -gt 0 ]; then
    echo "$failures check(s) failed"
    exit 1
fi
echo "All checks passed for: $*"
