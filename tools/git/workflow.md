# Рабочий процесс, настройки и сообщения Git

Откройте страницу, чтобы проверить правки, подготовить коммит или временно отложить работу.
[К справочнику Git](README.md).

| Задача | Приём | Пример |
| --- | --- | --- |
| Выбрать изменения для коммита | Сравнить рабочее дерево и индекс | [Карточка коммита](#посмотреть-изменения-и-подготовить-коммит) |
| Сменить задачу без коммита | Сохранить stash и проверить применение | [Карточка stash](#временно-отложить-работу) |
| Задать автора | Локальная конфигурация | [Настройки](#настроить-автора-и-интерфейс) |
| Сформулировать сообщение | Одна логическая задача | [Conventional Commits](#сообщения-коммитов) |
| Повторить весь процесс | Изолированный Bash-скрипт | [Полный сценарий](#проверяемый-рабочий-процесс) |

Уровни: базовый — коммит и настройки; средний — stash и ветки.
Предпосылки карточек: существующий репозиторий и настроенный автор.
Полный сценарий требует Bash и Git 2.32+ из-за изоляции `GIT_CONFIG_GLOBAL`.
Сверено с документацией: 2026-11-06, Git v2.55.0 и Conventional Commits 1.0.0.
Выполнено: 2026-11-06, Git 2.55.0, macOS, Bash 3.2.57; сценарий ниже.
Другие версии не запускались.

## Посмотреть изменения и подготовить коммит

**Ситуация:** нужно включить в коммит только проверенные изменения `app.py`.
Сравните рабочее дерево с индексом.
Затем сравните индекс с HEAD.

**Пример — фрагмент для вашего репозитория:**

```bash
git status --short
git diff -- app.py
git add -- app.py
git diff --staged
git diff --check --cached
git commit -m "fix: validate profile input"
git status --short
```

**Результат:** коммит содержит весь подготовленный снимок индекса.
Неподготовленные правки остаются в рабочем дереве.
Пустой итоговый `status --short` означает отсутствие видимых правок и новых неигнорируемых файлов.

**Ограничения:** `git add -- app.py` подготавливает все текущие изменения файла, включая удаление.
Для выбора отдельных фрагментов используйте `git add -p -- app.py`.
Перед коммитом проверьте весь `diff --staged`: индекс мог уже содержать другие файлы.
`git diff` не показывает содержимое новых неотслеживаемых файлов.
`git diff --check --cached` проверяет пробельные ошибки, но не поведение программы.
Запустите проверки проекта перед коммитом.
`git add .` может захватить лишние файлы внутри текущего каталога.
`.gitignore` не прекращает отслеживание уже добавленных файлов.

[Полный сценарий с веткой и merge](#проверяемый-рабочий-процесс) · [Убрать файл из индекса](history.md#убрать-файл-из-индекса)

## Временно отложить работу

**Ситуация:** нужно сменить задачу и сохранить незакоммиченные правки.
Выберите состав stash и способ восстановления.

| Требование | Команда | Ограничение |
| --- | --- | --- |
| Сохранить tracked и новые untracked | `git stash push -u -m "before switching task"` | Игнорируемые файлы остаются вне stash |
| Сохранить также ignored | `git stash push -a` | Может захватить локальные секреты и большие каталоги |
| Восстановить с сохранением записи | `git stash apply 'stash@{0}'` | Возможен конфликт; разделение staged/unstaged не восстанавливается полностью |
| Попытаться восстановить также индекс | `git stash apply --index 'stash@{0}'` | При конфликте восстановление индекса может не удаться |

**Пример — фрагмент для репозитория с правками и хотя бы одним коммитом:**

```bash
git status --short
git stash push -u -m "before switching task"
git stash list
git stash show -u --stat 'stash@{0}'
```

**Результат:** при наличии сохраняемых правок Git создаёт запись stash и убирает эти правки из рабочего дерева и индекса.
После временной задачи вернитесь в нужную ветку.
Убедитесь, что рабочее дерево и индекс чистые.
Выберите нужную запись по `git stash list`.
Следующий фрагмент предполагает, что нужная запись всё ещё `stash@{0}`:

```bash
git stash apply 'stash@{0}'
git status --short
git diff
git diff --staged
```

- [ ] Проверьте восстановленные новые файлы.
- [ ] Разрешите конфликты, если они появились.
- [ ] Выполните проверки проекта.

Только после проверки удалите именно применённую запись:

```bash
git stash drop 'stash@{0}'
```

**Последствия:** `drop` удаляет запись восстановления и оставляет восстановленные файлы.
Новая запись stash меняет номера старых записей.
Если сохраняемых правок не было, `push` не создаст запись: `stash@{0}` может указывать на прежнюю работу.
`pop` совмещает применение и удаление при успехе.
При конфликте `pop` оставляет запись.
У stash нет команды `--abort`; не сбрасывайте конфликтующие файлы без проверки сохранности работы.

[Полный сценарий с проверкой stash](#проверяемый-рабочий-процесс)

## Настроить автора и интерфейс

Фрагмент предназначен для вашего репозитория.
Замените значения своими.
Без `--global` настройки относятся только к этому репозиторию.

```bash
git config user.name "Example Developer"
git config user.email "developer@example.invalid"
git config core.editor "nano"
git config --list --show-origin
```

`--global` меняет настройки всех ваших репозиториев.
Email может попасть в публичную историю.
Для GitHub можно использовать предоставленный сервисом адрес noreply.
Авторство не даёт права push.

Алиасы — необязательный фрагмент конфигурации `.git/config` этого репозитория:

```ini
[alias]
    st = status
    ci = commit
    br = branch
    co = checkout
    lg = log --oneline --graph --all
    last = log -1 HEAD
    unstage = restore --staged --
```

`checkout` остаётся действующей командой. Для новых примеров удобнее разделять
`switch` (ветки) и `restore` (файлы), чтобы не смешивать две задачи.

## Сообщения коммитов

Ниже приведён формат соглашения Conventional Commits.
Это шаблон текста, а не команда:

```text
type(scope)!: краткое описание

Почему понадобилось изменение и что теперь происходит.

BREAKING CHANGE: описание несовместимости и пути перехода
Closes #123
```

`scope` и `!` необязательны.
`!` или footer `BREAKING CHANGE:` обозначают несовместимое изменение.
Просто высокая важность правки не является основанием для этих обозначений.
`feat` обозначает возможность.
`fix` обозначает исправление.
Команда также может договориться о `docs`, `style`, `refactor`, `test`, `build`, `ci`, `chore`.
Соглашение не требует жёсткой длины 50/72 символа.
Ограничения заголовка задаёт проект.

Пример законченного сообщения:

```text
fix(api): reject empty usernames

Пустое имя раньше сохранялось и приводило к ошибке при входе.
Проверяем его до сохранения и возвращаем понятную ошибку.

Fixes #78
```

Согласуйте язык сообщений и наклонение с проектом.
«Правки» и «Ещё коммит» не объясняют задачу.
`git commit -v` показывает staged diff в редакторе.
Не добавляйте несвязанные изменения в один коммит.

## Проверяемый рабочий процесс

Полный пример создаёт только временный каталог с синтетическими файлами.
При выходе пример удаляет этот каталог.
Пример не использует сеть и личный remote.
Пример не меняет глобальную конфигурацию.
Сохраните блок как `workflow.sh`.
Запустите `bash workflow.sh`.

<!-- example: git/workflow.sh -->
```bash
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
```

**Результат:** два обычных коммита и merge-коммит с двумя родителями.
Проверки подтверждают сохранение tracked/untracked и сохранность записи после `apply`.
Игнорируемый файл остаётся вне stash.
После учебной очистки рабочее дерево чистое, а локальная feature-ветка удалена.
Скрипт выводит `workflow OK`.
Очистка касается только созданного временного каталога.

## Источники

- [Git v2.55.0: add](https://raw.githubusercontent.com/git/git/v2.55.0/Documentation/git-add.adoc), [status](https://raw.githubusercontent.com/git/git/v2.55.0/Documentation/git-status.adoc), [diff](https://raw.githubusercontent.com/git/git/v2.55.0/Documentation/git-diff.adoc).
- [Config](https://raw.githubusercontent.com/git/git/v2.55.0/Documentation/git-config.adoc), [stash](https://git-scm.com/docs/git-stash/2.55.0), [merge](https://raw.githubusercontent.com/git/git/v2.55.0/Documentation/git-merge.adoc).
- [Изоляция конфигурации в Git 2.32](https://raw.githubusercontent.com/git/git/v2.32.0/Documentation/RelNotes/2.32.0.txt), [release notes 2.55.0](https://raw.githubusercontent.com/git/git/v2.55.0/Documentation/RelNotes/2.55.0.adoc).
- [Conventional Commits 1.0.0](https://www.conventionalcommits.org/en/v1.0.0/).
