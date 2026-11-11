#!/usr/bin/env bash
set -euo pipefail
task_dir=$(mktemp -d "${TMPDIR:-/tmp}/uv-project.XXXXXX")
trap 'rm -rf -- "$task_dir"' EXIT
export UV_CACHE_DIR="$task_dir/cache" UV_PYTHON_DOWNLOADS=never
export UV_NO_CONFIG=1
python_bin=$(command -v python3)
uv init --bare --no-workspace --python "$python_bin" "$task_dir/project"
cd "$task_dir/project"
uv lock --offline --python "$python_bin"
uv sync --offline --locked --python "$python_bin"
uv run --offline --locked python -c 'import sys; assert sys.prefix != sys.base_prefix; print("venv OK")'
uv export --offline --locked --format requirements.txt -o requirements.txt
cp pyproject.toml pyproject.saved
"$python_bin" - <<'EDIT'
from pathlib import Path
p = Path('pyproject.toml')
text = p.read_text()
assert 'version = "0.1.0"' in text
p.write_text(text.replace('version = "0.1.0"', 'version = "0.2.0"'))
EDIT
if uv sync --offline --locked >"$task_dir/stale.log" 2>&1; then
    printf 'ERROR: stale lock accepted\n' >&2
    exit 1
fi
grep -q 'lockfile.*needs to be updated' "$task_dir/stale.log"
mv pyproject.saved pyproject.toml
uv sync --offline --locked
printf 'uv project OK\n'
