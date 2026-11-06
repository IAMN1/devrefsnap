# Рабочий процесс, настройки и сообщения Git

Уровень: базовый и средний.
Предпосылки полного сценария: Git 2.32+, Bash, доступный временный каталог.
Именно с [2.32](https://raw.githubusercontent.com/git/git/v2.32.0/Documentation/RelNotes/2.32.0.txt)
доступна используемая изоляция `GIT_CONFIG_GLOBAL`.
Проверка выполнена на Git 2.55.0.
[К справочнику Git](README.md).

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

## Проверяемый рабочий процесс

Полный пример создаёт только временный каталог.
При выходе пример удаляет этот каталог.
Пример не использует сеть и личный remote.
Пример не меняет глобальную конфигурацию.
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
git switch -q main
git merge -q --no-ff feature/profile -m "Merge profile feature"
git branch -d feature/profile
test "$(git rev-list --count HEAD)" -eq 3
grep -qx 'profile' greeting.txt
test -z "$(git status --porcelain)"
git log --oneline --graph --all
printf 'workflow OK\n'
```

Результат: два обычных коммита и merge-коммит с двумя родителями.
Рабочее дерево чистое.
Локальная feature-ветка удалена.
Скрипт выводит `workflow OK`.
Удаление каталога касается только созданной копии.

## Временно отложить работу

Фрагмент для существующего репозитория с незакоммиченными правками:

```bash
git stash push -u -m "before switching task"
git stash list
git stash show --stat 'stash@{0}'
git stash apply 'stash@{0}'
```

После проверки восстановленных файлов запись можно удалить через `git stash drop 'stash@{0}'`.
`apply` и `pop` не гарантируют отсутствие конфликтов.
Перед применением убедитесь, что текущая ветка подходит.
`stash drop` убирает запись восстановления, а не файлы из рабочего дерева.

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

## Источники

[git-config](https://git-scm.com/docs/git-config), [git-add](https://git-scm.com/docs/git-add),
[git-merge](https://git-scm.com/docs/git-merge), [git-stash](https://git-scm.com/docs/git-stash),
[Conventional Commits](https://www.conventionalcommits.org/en/v1.0.0/).
