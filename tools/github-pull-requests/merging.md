# Синхронизация, слияние и очистка веток

Уровень: средний и продвинутый. Предпосылки: merge/rebase в Git и права на целевой репозиторий.
[К справочнику Pull Requests](README.md).

## Обновить свою ветку

Фрагмент для существующего проекта; сначала сохрани локальную работу и проверь ветку.

```text
git switch feature/profile
git fetch origin
git log --oneline --left-right HEAD...origin/main
git merge origin/main
```

После разрешения конфликтов: `git add -- file` и `git merge --continue`; отмена — `git merge --abort`.
Альтернатива по соглашению команды — `git rebase origin/main`: переписывает свою ветку,
а для конфликтов нужны `rebase --continue` / `--abort`, не произвольный новый merge-коммит.
После опубликованного rebase требуется согласованный push с [проверкой lease](../git/remotes.md).
Не перебазируй общую интеграционную ветку только ради привычной линейности.

## Выбрать способ слияния

| Метод GitHub | Результат | Когда уместен |
| --- | --- | --- |
| Merge commit | Сохраняет коммиты head и добавляет merge-коммит | Важны исходные коммиты и топология |
| Squash and merge | Итоговое изменение попадает в один новый коммит | PR — одна логическая задача, промежуточные коммиты не нужны |
| Rebase and merge | Переприменяет коммиты в base с новыми SHA | Нужны отдельные коммиты и линейная история |

Доступность методов задаётся настройками репозитория и правилами ветки.
GitHub rebase-and-merge не тождественен последовательности `git rebase main; git merge`:
последняя без ветки у merge использует upstream текущей ветки и не описывает интеграцию в main.
Локальный `git merge --squash feature` только готовит индекс и рабочее дерево; затем нужен `git commit`.
Не обходи GitHub-проверки локальным merge и прямым push в защищённую base.

Справочный CLI-фрагмент, **внешнее изменение, не выполнялся**:

```text
gh pr merge 123 --squash
```

До запуска убедись, что выбран нужный PR, окончательный diff проверен и разрешено слияние.
При merge queue используй предусмотренный репозиторием процесс очереди.

## Проверить результат и удалить ненужную ветку

После merge проверь состояние PR и, если применимо, результат деплоя. Затем можно обновить main.
Ниже отдельные справочные операции: remote delete меняет общий репозиторий.

```text
git switch main
git pull --ff-only
git branch --merged main
git branch -d feature/profile
git push origin --delete feature/profile
git fetch --prune origin
```

`branch -d` проверяет слитость по Git-истории; после squash это не всегда выполняется.
Если он отказался, изучи `git log main..feature/profile`, diff и итог PR.
Принудительное локальное `-D` допустимо только после осознанной проверки сохранности работы.
Исчезнувший remote/upstream (`gone`) не доказывает, что локальная ветка больше не нужна.

## Разобраться с неправильным списком коммитов

Проверь base, head и их репозитории; затем `git log --oneline --graph --all` и merge-base.
Текущие ahead/behind локально показывает `git rev-list --left-right --count origin/main...HEAD`
после `fetch`: слева — коммиты только base, справа — только head.
История переписанной ветки автоматически отражается в PR; старые комментарии могут стать outdated.
Если после force push содержимое неожиданно изменилось, сохрани ссылки на нужные коммиты и выясни причину
до повторной перезаписи. [Reflog](../git/history.md) помогает изучить локальные прежние состояния.

## Источники и границы проверки

[Merge methods](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/configuring-pull-request-merges/about-merge-methods-on-github),
[CLI merge](https://cli.github.com/manual/gh_pr_merge), [git merge](https://git-scm.com/docs/git-merge),
[git branch](https://git-scm.com/docs/git-branch).
Сверка: 2026-11-06. Слияния и удаления веток на GitHub не выполнялись; синтетические Git-сценарии — [в теме Git](../git/README.md).
