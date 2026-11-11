#!/usr/bin/env bash
set -euo pipefail
task_dir=$(mktemp -d "${TMPDIR:-/tmp}/git-conflicts.XXXXXX")
trap 'rm -rf -- "$task_dir"' EXIT
export GIT_CONFIG_NOSYSTEM=1 GIT_CONFIG_GLOBAL=/dev/null
export GIT_AUTHOR_NAME=Demo GIT_AUTHOR_EMAIL=demo@example.invalid
export GIT_COMMITTER_NAME=Demo GIT_COMMITTER_EMAIL=demo@example.invalid
export GIT_CONFIG_COUNT=2
export GIT_CONFIG_KEY_0=commit.gpgsign GIT_CONFIG_VALUE_0=false
export GIT_CONFIG_KEY_1=core.hooksPath GIT_CONFIG_VALUE_1=/dev/null
export GIT_EDITOR=true

git init -q -b main "$task_dir/project"
cd "$task_dir/project"
printf 'base
' > note.txt
git add -- note.txt
git commit -qm "feat: base"
git switch -q -c feature
printf 'feature
' > note.txt
git commit -qam "feat: feature version"
feature_tip=$(git rev-parse HEAD)
git switch -q main
printf 'main
' > note.txt
git commit -qam "feat: main version"
main_tip=$(git rev-parse HEAD)

git switch -q -c merge-demo feature
if git merge main --no-edit; then
    printf 'ERROR: expected merge conflict
' >&2
    exit 1
fi
test -n "$(git ls-files -u)"
git merge --abort
test "$(git rev-parse HEAD)" = "$feature_tip"
test "$(cat note.txt)" = feature
if git merge main --no-edit; then
    exit 1
fi
printf 'main and feature
' > note.txt
git add -- note.txt
git merge --continue
test "$(git rev-parse HEAD^1)" = "$feature_tip"
test "$(git rev-parse HEAD^2)" = "$main_tip"
test "$(cat note.txt)" = 'main and feature'
test -z "$(git status --porcelain)"

git switch -q feature
if git rebase main; then
    printf 'ERROR: expected rebase conflict
' >&2
    exit 1
fi
test -n "$(git ls-files -u)"
git rebase --abort
test "$(git rev-parse HEAD)" = "$feature_tip"
test "$(cat note.txt)" = feature
if git rebase main; then
    exit 1
fi
printf 'main and feature
' > note.txt
git add -- note.txt
git rebase --continue
test "$(git rev-parse HEAD^)" = "$main_tip"
test "$(git rev-parse HEAD)" != "$feature_tip"
test "$(cat note.txt)" = 'main and feature'
test -z "$(git status --porcelain)"
printf 'conflicts OK
'
