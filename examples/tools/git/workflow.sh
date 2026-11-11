#!/usr/bin/env bash
set -euo pipefail
task_dir=$(mktemp -d "${TMPDIR:-/tmp}/git-workflow.XXXXXX")
trap 'rm -rf -- "$task_dir"' EXIT
export GIT_CONFIG_NOSYSTEM=1 GIT_CONFIG_GLOBAL=/dev/null
export GIT_AUTHOR_NAME=Demo GIT_AUTHOR_EMAIL=demo@example.invalid
export GIT_COMMITTER_NAME=Demo GIT_COMMITTER_EMAIL=demo@example.invalid
export GIT_CONFIG_COUNT=2
export GIT_CONFIG_KEY_0=commit.gpgsign GIT_CONFIG_VALUE_0=false
export GIT_CONFIG_KEY_1=core.hooksPath GIT_CONFIG_VALUE_1=/dev/null

git init -q -b main "$task_dir/project"
cd "$task_dir/project"
printf '.venv/\n*.log\n' > .gitignore
printf 'hello\n' > greeting.txt
git add -- .gitignore greeting.txt
git diff --staged --stat
git commit -q -m "feat: add greeting"
git switch -q -c feature/profile
printf 'profile\n' >> greeting.txt
git diff -- greeting.txt
git add -- greeting.txt
git commit -q -m "feat: add profile greeting"
# Stash сохраняет tracked и untracked; ignored остаётся на месте.
printf 'draft\n' >> greeting.txt
printf 'new\n' > draft.txt
printf 'ignored\n' > local.log
git stash push -q -u -m "before switching task"
test "$(git stash list | wc -l | tr -d ' ')" -eq 1
test ! -e draft.txt
test -e local.log
test -z "$(git status --porcelain)"
git stash apply -q 'stash@{0}'
grep -qx 'draft' greeting.txt
test -e draft.txt
test "$(git stash list | wc -l | tr -d ' ')" -eq 1
# Правки проверены. Drop удаляет запись, а не восстановленные файлы.
git stash drop -q 'stash@{0}'
test -z "$(git stash list)"
test -e draft.txt
# Очистка нужна только для продолжения этого учебного сценария.
git restore -- greeting.txt
rm -- draft.txt local.log
git switch -q main
git merge -q --no-ff feature/profile -m "Merge profile feature"
git branch -d feature/profile
test "$(git rev-list --count HEAD)" -eq 3
grep -qx 'profile' greeting.txt
test -z "$(git status --porcelain)"
git log --oneline --graph --all
printf 'workflow OK\n'
