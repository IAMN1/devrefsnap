# Отмена изменений, восстановление и rebase

Уровень: средний и продвинутый. Предпосылки: понимание индекса, коммитов и веток.
[К справочнику Git](README.md).

## Выбрать операцию

Следующие команды — отдельные фрагменты, а не последовательность для копирования целиком.

| Команда | HEAD | Индекс | Рабочее дерево |
| --- | --- | --- | --- |
| `restore --staged -- file` | Без изменения | Версия из HEAD | Без изменения |
| `restore -- file` | Без изменения | Без изменения | Версия из индекса; незакоммиченный текст файла теряется |
| `reset --soft HEAD~1` | На родителя | Сохраняется | Сохраняется |
| `reset --mixed HEAD~1` | На родителя | Версия родителя | Сохраняется |
| `reset --hard HEAD~1` | На родителя | Версия родителя | Версия родителя; локальные правки отслеживаемых файлов теряются |
| `revert COMMIT` | Новый обратный коммит | Обновляется | Обновляется |

`reset --hard` может удалить неотслеживаемые пути, мешающие записи отслеживаемого файла.
Он не стирает объект коммита немедленно: прежний HEAD может быть в reflog, пока объекты не очищены.
Reflog хранит движения ссылок, но не каждый незакоммиченный текст и не является долговечным backup.
Для общей опубликованной истории обычно выбирают `revert`.

## Проверить режимы reset и revert

Полный учебный Bash-скрипт; его разрушительные операции ограничены временным репозиторием.
Запуск: `bash history.sh`. Никакие пользовательские ветки не затрагиваются.

<!-- example: git/history.sh -->
```bash
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
git branch rescue "$changed"

git reset -q --soft "$base"
test "$(git show :note.txt)" = changed
test "$(cat note.txt)" = changed
git reset -q --mixed "$base"
test "$(git show :note.txt)" = base
test "$(cat note.txt)" = changed
git restore -- note.txt
test "$(cat note.txt)" = base

git reset -q --hard "$changed"
printf 'uncommitted\n' > note.txt
git reset -q --hard "$base"
test "$(cat note.txt)" = base
git reset -q --hard rescue
git revert --no-edit "$changed" >/dev/null
test "$(cat note.txt)" = base
test "$(git rev-list --count HEAD)" -eq 3
git reflog -5
printf 'history OK\n'
```

Результат: проверки различий HEAD/индекса/файла проходят, revert добавляет третий коммит,
выводится `history OK`. В реальном проекте перед опасной операцией сохрани работу отдельным
коммитом или копией, затем создай `git branch rescue COMMIT`. Восстановление через новую ветку
позволяет изучить коммит до любого reset текущей ветки.

## Исправить свой последний коммит

Фрагмент: только после просмотра staged diff. `amend` создаёт новый SHA.

```bash
git add -- app.py
git diff --staged
git commit --amend --no-edit
```

Чтобы изменить сообщение, убери `--no-edit`. Уже опубликованную ветку после amend придётся
переписать; последствия и проверка ожидаемого remote SHA — в [remotes.md](remotes.md).

## Перебазировать свою ветку

Фрагмент: текущая ветка `feature/profile`, рабочее дерево чистое, remote `origin` уже настроен.

```bash
git fetch origin
git branch backup-before-rebase
git rebase origin/main
```

При конфликте: исправь файл, `git add -- file`, затем `git rebase --continue`.
Для возврата к состоянию перед незавершённым rebase — `git rebase --abort`.
`--skip` пропускает текущий коммит и может потерять его изменение; это отдельное решение.
Интерактивный `git rebase -i HEAD~3` позволяет редактировать порядок и объединять коммиты
через `squash`/`fixup`; сначала проверь, что три коммита принадлежат твоей неопубликованной работе.

После успешного rebase сравни diff и запусти проверки; линейная история не доказывает эквивалентность поведения.
Полный проверенный сценарий rebase и lease — [на странице удалённых веток](remotes.md).

## Источники

[reset](https://git-scm.com/docs/git-reset), [restore](https://git-scm.com/docs/git-restore),
[revert](https://git-scm.com/docs/git-revert), [reflog](https://git-scm.com/docs/git-reflog),
[rebase](https://git-scm.com/docs/git-rebase).
