#!/usr/bin/env bash
set -euo pipefail
task_dir=$(mktemp -d "${TMPDIR:-/tmp}/linux-files.XXXXXX")
trap 'rm -rf -- "$task_dir"' EXIT
mkdir "$task_dir/source" "$task_dir/restored"
printf 'INFO started\nERROR missing\nINFO done\n' > "$task_dir/source/app log.txt"
cp "$task_dir/source/app log.txt" "$task_dir/source/copy.txt"
cmp "$task_dir/source/app log.txt" "$task_dir/source/copy.txt"
mv "$task_dir/source/copy.txt" "$task_dir/source/renamed.txt"
test "$(grep -c '^INFO' "$task_dir/source/app log.txt")" -eq 2
test "$(awk '$1 == "ERROR" {print $2}' "$task_dir/source/app log.txt")" = missing
find "$task_dir/source" -type f -name '*.txt' -exec wc -l {} +
tar -cf "$task_dir/logs.tar" -C "$task_dir" source
tar -xf "$task_dir/logs.tar" -C "$task_dir/restored"
cmp "$task_dir/source/app log.txt" "$task_dir/restored/source/app log.txt"
gzip -c "$task_dir/source/app log.txt" > "$task_dir/log.txt.gz"
gzip -cd "$task_dir/log.txt.gz" | cmp "$task_dir/source/app log.txt" -
chmod u=rw,go= "$task_dir/source/app log.txt"
printf 'files OK\n'
