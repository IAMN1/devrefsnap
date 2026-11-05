# Удалённые ветки и force-with-lease

Уровень: средний и продвинутый. Предпосылки: ветки, merge, rebase; рабочее дерево сохранено.
[К справочнику Git](README.md).

## Получить изменения и выбрать интеграцию

Фрагменты для существующего проекта; URL и ветки требуют реальных значений.

```text
git remote add origin URL
git remote -v
git push -u origin main
git fetch origin
git log --oneline --left-right main...origin/main
git pull --ff-only
```

`fetch` обновляет remote-tracking ссылки, не сливая их в текущую ветку.
`pull` получает и интегрирует изменения; `--ff-only` отказывает при расхождении вместо создания merge.
Не запускай pull автоматически в неизвестной ветке. `push -u` задаёт upstream; обычный `push`
зависит от конфигурации. В репозитории с PR прямой push в main может быть запрещён.

Для fork добавляют `upstream` с URL исходного проекта, делают `git fetch upstream`,
затем на локальной `main` — `git merge --ff-only upstream/main`, если история допускает fast-forward.
При собственных коммитах выбери согласованный merge/rebase; remote `origin` остаётся твоим fork.

## Переписать свою ветку с проверкой

`--force` может затереть чужое продвижение ветки. `--force-with-lease` отклоняет push,
если remote не совпал с ожидаемым состоянием. Вариант без ожидаемого SHA опирается на локальную
remote-tracking ссылку; фоновый fetch способен изменить эту опору.
Явное `--force-with-lease=refs/heads/feature:EXPECTED_SHA` задаёт проверяемую версию точно.
Не обновляй EXPECTED_SHA автоматически после отказа: сначала выясни, кто и что запушил.

Полный пример создаёт только локальный bare remote и две учебные копии. Проверяет успешный rebase,
принятый lease и отклонение устаревшего lease. Запуск: `bash remotes.sh`.

<!-- example: git/remotes.sh -->
```bash
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
printf 'remote lease OK\n'
```

Ожидается `remote lease OK`; сообщение `stale info` проверяется как ожидаемый отказ.
Никаких GitHub действий и пользовательских remote этот тест не выполняет.

## Удалить ветку после проверки результата

Фрагменты: сначала перейди в другую ветку, проверь merge/PR и отсутствие нужных локальных коммитов.

```text
git switch main
git branch --merged main
git branch -d feature/profile
git push origin --delete feature/profile
git fetch --prune origin
```

Удаление remote-ветки меняет общий репозиторий. `fetch --prune` убирает устаревшие remote-tracking
ссылки, но не удаляет локальные ветки. После squash `branch -d` может отказать: проверь содержимое
и сохранность работы, затем решай отдельно. Не удаляй все ветки с `gone` через конвейер `branch -D`.

## Источники

[fetch](https://git-scm.com/docs/git-fetch), [pull](https://git-scm.com/docs/git-pull),
[push](https://git-scm.com/docs/git-push), [branch](https://git-scm.com/docs/git-branch).
