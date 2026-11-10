: ; unset VIRTUAL_ENV; [ $# -gt 0 ] || set -- --list; exec uv run python _CI/lib/vendor/bin/invoke --search-root _CI "$@"
@setlocal
@set "VIRTUAL_ENV="
@set WORKFLOW_ARGS=%*
@if not defined WORKFLOW_ARGS set WORKFLOW_ARGS=--list
@uv run python _CI\lib\vendor\bin\invoke --search-root _CI %WORKFLOW_ARGS%
