# Отмена изменений, восстановление и rebase

Уровень: средний и продвинутый.
Предпосылки: понимание индекса, коммитов и веток.
[К справочнику Git](README.md).

## Выбрать операцию

Следующие команды — отдельные фрагменты.
Не копируйте все команды как одну последовательность.

| Команда | HEAD | Индекс | Рабочее дерево |
| --- | --- | --- | --- |
| `restore --staged -- file` | Без изменения | Версия из HEAD | Без изменения |
| `restore -- file` | Без изменения | Без изменения | Версия из индекса. Незакоммиченный текст файла теряется |
| `reset --soft HEAD~1` | На родителя | Сохраняется | Сохраняется |
| `reset --mixed HEAD~1` | На родителя | Версия родителя | Сохраняется |
| `reset --hard HEAD~1` | На родителя | Версия родителя | Версия родителя. Локальные правки отслеживаемых файлов теряются |
| `revert COMMIT` | Новый обратный коммит | Обновляется | Обновляется |

`reset --hard` может удалить неотслеживаемые пути, мешающие записи отслеживаемого файла.
`reset --hard` не стирает объект коммита немедленно.
Пока объекты не очищены, прежний HEAD может быть в reflog.
Reflog хранит движения ссылок.
Reflog не хранит каждый незакоммиченный текст и не является долговечной резервной копией.
Для общей опубликованной истории обычно выбирают `revert`.

## Проверить режимы reset и revert

Ниже приведён полный учебный Bash-скрипт.
Разрушительные операции скрипта ограничены временным репозиторием.
Запустите `bash history.sh`.
Скрипт не затрагивает пользовательские ветки.

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

Результат: проверки различий HEAD/индекса/файла проходят.
Revert добавляет третий коммит.
Скрипт выводит `history OK`.
В реальном проекте перед опасной операцией сохраните работу отдельным коммитом или копией.
Затем создайте ветку через `git branch rescue COMMIT`.
Восстановление через новую ветку позволяет изучить коммит до любого reset текущей ветки.

## Исправить свой последний коммит

Используйте фрагмент только после просмотра staged diff.
`amend` создаёт новый SHA.

```bash
git add -- app.py
git diff --staged
git commit --amend --no-edit
```

Чтобы изменить сообщение, уберите `--no-edit`.
После amend уже опубликованную ветку придётся переписать.
Последствия и проверка ожидаемого remote SHA описаны в [remotes.md](remotes.md).

## Перебазировать свою ветку

Предпосылки фрагмента: текущая ветка `feature/profile`, чистое рабочее дерево и настроенный remote `origin`.

```bash
git fetch origin
git branch backup-before-rebase
git rebase origin/main
```

При конфликте исправьте файл.
Выполните `git add -- file`.
Затем выполните `git rebase --continue`.
Для возврата к состоянию перед незавершённым rebase выполните `git rebase --abort`.
`--skip` пропускает текущий коммит.
Эта операция может потерять изменение коммита и требует отдельного решения.
Интерактивный `git rebase -i HEAD~3` позволяет редактировать порядок коммитов.
Через `squash`/`fixup` можно объединять коммиты.
Сначала проверьте, что три коммита принадлежат вашей неопубликованной работе.

После успешного rebase сравните diff.
Запустите проверки.
Линейная история не доказывает эквивалентность поведения.
Полный проверенный сценарий rebase и lease — [на странице удалённых веток](remotes.md).

## Источники

[reset](https://git-scm.com/docs/git-reset), [restore](https://git-scm.com/docs/git-restore),
[revert](https://git-scm.com/docs/git-revert), [reflog](https://git-scm.com/docs/git-reflog),
[rebase](https://git-scm.com/docs/git-rebase).
