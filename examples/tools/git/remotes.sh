#!/usr/bin/env bash
set -euo pipefail
task_dir=$(mktemp -d "${TMPDIR:-/tmp}/git-remotes.XXXXXX")
trap 'rm -rf -- "$task_dir"' EXIT
export GIT_CONFIG_NOSYSTEM=1 GIT_CONFIG_GLOBAL=/dev/null
export GIT_AUTHOR_NAME=Demo GIT_AUTHOR_EMAIL=demo@example.invalid
export GIT_COMMITTER_NAME=Demo GIT_COMMITTER_EMAIL=demo@example.invalid
export GIT_CONFIG_COUNT=2
export GIT_CONFIG_KEY_0=commit.gpgsign GIT_CONFIG_VALUE_0=false
export GIT_CONFIG_KEY_1=core.hooksPath GIT_CONFIG_VALUE_1=/dev/null
export LC_ALL=C

git init -q --bare -b main "$task_dir/remote.git"
git clone -q "$task_dir/remote.git" "$task_dir/alice"
cd "$task_dir/alice"
printf 'base\n' > base.txt
git add base.txt
git commit -q -m "feat: base"
git push -q -u origin main
git switch -q -c feature
printf 'feature\n' > feature.txt
git add feature.txt
git commit -q -m "feat: feature"
git push -q -u origin feature
expected=$(git rev-parse origin/feature)
git switch -q main
printf 'main update\n' > main.txt
git add main.txt
git commit -q -m "docs: main update"
git push -q origin main
git switch -q feature
git rebase main >/dev/null
git merge-base --is-ancestor main feature
git push -q --force-with-lease="refs/heads/feature:$expected" origin HEAD:feature
expected=$(git rev-parse HEAD)

git clone -q "$task_dir/remote.git" "$task_dir/bob"
git -C "$task_dir/bob" switch -q feature
printf 'bob\n' > "$task_dir/bob/bob.txt"
git -C "$task_dir/bob" add bob.txt
git -C "$task_dir/bob" commit -q -m "docs: bob update"
git -C "$task_dir/bob" push -q origin feature

if git push --force-with-lease="refs/heads/feature:$expected" origin HEAD:feature >"$task_dir/rejected.log" 2>&1; then
    printf 'ERROR: stale lease unexpectedly accepted\n' >&2
    exit 1
fi
grep -q 'stale info' "$task_dir/rejected.log"
# Даже после fetch ожидаемый SHA остаётся прежним и защищает от перезаписи Bob.
git fetch -q origin
test "$(git rev-parse origin/feature)" != "$expected"
if git push --force-with-lease="refs/heads/feature:$expected" origin HEAD:feature >"$task_dir/rejected-after-fetch.log" 2>&1; then
    printf 'ERROR: stale explicit lease accepted after fetch\n' >&2
    exit 1
fi
grep -q 'stale info' "$task_dir/rejected-after-fetch.log"
test "$(git --git-dir="$task_dir/remote.git" rev-parse refs/heads/feature)" = "$(git -C "$task_dir/bob" rev-parse HEAD)"

# Удаляем только заведомо интегрированную учебную ветку.
git switch -q main
git switch -q -c cleanup-demo
printf 'cleanup\n' > cleanup.txt
git add -- cleanup.txt
git commit -qm "docs: cleanup demo"
git push -q -u origin cleanup-demo
git -C "$task_dir/bob" fetch -q origin
git -C "$task_dir/bob" show-ref --verify --quiet refs/remotes/origin/cleanup-demo
git switch -q main
git merge -q --no-ff cleanup-demo -m "Merge cleanup demo"
git merge-base --is-ancestor cleanup-demo main
git push -q origin main
git merge-base --is-ancestor cleanup-demo origin/main
test "$(git --git-dir="$task_dir/remote.git" show main:cleanup.txt)" = cleanup
git branch -d cleanup-demo
git push -q origin --delete cleanup-demo
git -C "$task_dir/bob" fetch -q --prune origin
if git -C "$task_dir/bob" show-ref --verify --quiet refs/remotes/origin/cleanup-demo; then
    printf 'ERROR: obsolete tracking ref survived prune\n' >&2
    exit 1
fi
test "$(cat cleanup.txt)" = cleanup
test "$(git -C "$task_dir/bob" show origin/main:cleanup.txt)" = cleanup
printf 'remote lease and cleanup OK\n'
