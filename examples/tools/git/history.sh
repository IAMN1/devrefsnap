#!/usr/bin/env bash
set -euo pipefail
task_dir=$(mktemp -d "${TMPDIR:-/tmp}/git-history.XXXXXX")
trap 'rm -rf -- "$task_dir"' EXIT
export GIT_CONFIG_NOSYSTEM=1 GIT_CONFIG_GLOBAL=/dev/null
export GIT_AUTHOR_NAME=Demo GIT_AUTHOR_EMAIL=demo@example.invalid
export GIT_COMMITTER_NAME=Demo GIT_COMMITTER_EMAIL=demo@example.invalid
export GIT_CONFIG_COUNT=2
export GIT_CONFIG_KEY_0=commit.gpgsign GIT_CONFIG_VALUE_0=false
export GIT_CONFIG_KEY_1=core.hooksPath GIT_CONFIG_VALUE_1=/dev/null

git init -q -b main "$task_dir/project"
cd "$task_dir/project"
printf 'base\n' > note.txt
git add note.txt
git commit -q -m "feat: add base"
base=$(git rev-parse HEAD)
printf 'changed\n' > note.txt
git commit -qam "fix: change note"
changed=$(git rev-parse HEAD)
# У файла разные версии в HEAD, индексе и рабочем дереве.
printf 'staged\n' > note.txt
git add -- note.txt
printf 'unstaged\n' > note.txt
git restore --staged -- note.txt
test "$(git show :note.txt)" = changed
test "$(cat note.txt)" = unstaged
git restore -- note.txt
test "$(cat note.txt)" = changed
printf 'staged\n' > note.txt
git add -- note.txt
printf 'unstaged\n' > note.txt
git restore --source=HEAD --staged --worktree -- note.txt
test "$(git show :note.txt)" = changed
test "$(cat note.txt)" = changed

git reset -q --soft "$base"
test "$(git show :note.txt)" = changed
test "$(cat note.txt)" = changed
git reset -q --hard "$changed"
git reset -q --mixed "$base"
test "$(git show :note.txt)" = base
test "$(cat note.txt)" = changed
git restore -- note.txt
test "$(cat note.txt)" = base

git reset -q --hard "$changed"
printf 'uncommitted\n' > note.txt
git reset -q --hard "$base"
test "$(cat note.txt)" = base
# Находим сохранённый объект через локальный reflog, затем создаём ссылку.
lost=$(git reflog --format=%H --grep-reflog='commit: fix: change note' -1)
test "$lost" = "$changed"
git show --stat "$lost"
git branch rescue "$lost"
test "$(git rev-parse rescue)" = "$changed"
git reset -q --hard rescue
git revert --no-edit "$changed" >/dev/null
test "$(cat note.txt)" = base
test "$(git rev-list --count HEAD)" -eq 3
git reflog -5
printf 'history OK\n'
