# Синхронизация, слияние и очистка веток

Уровень: средний и продвинутый.
Предпосылки: merge/rebase в Git и права на целевой репозиторий.
[К справочнику Pull Requests](README.md).

## Обновить свою ветку

Фрагмент предназначен для существующего проекта.
Сначала сохраните локальную работу.
Проверьте текущую ветку.

```text
git switch feature/profile
git fetch origin
git log --oneline --left-right HEAD...origin/main
git merge origin/main
```

После разрешения конфликтов выполните `git add -- file`.
Затем выполните `git merge --continue`.
Для отмены выполните `git merge --abort`.
По соглашению команды можно использовать альтернативу: `git rebase origin/main`.
Rebase переписывает вашу ветку.
Для конфликтов rebase используйте `rebase --continue` / `--abort`.
Не создавайте вместо этого произвольный новый merge-коммит.
После опубликованного rebase требуется согласованный push с [проверкой lease](../git/remotes.md).
Не перебазируйте общую интеграционную ветку только ради привычной линейности.

## Выбрать способ слияния

| Метод GitHub | Результат | Когда уместен |
| --- | --- | --- |
| Merge commit | Сохраняет коммиты head и добавляет merge-коммит | Важны исходные коммиты и топология |
| Squash and merge | Итоговое изменение попадает в один новый коммит | PR — одна логическая задача, промежуточные коммиты не нужны |
| Rebase and merge | Переприменяет коммиты в base с новыми SHA | Нужны отдельные коммиты и линейная история |

Доступность методов задаётся настройками репозитория и правилами ветки.
GitHub rebase-and-merge не тождественен последовательности `git rebase main; git merge`:
последняя без ветки у merge использует upstream текущей ветки и не описывает интеграцию в main.
Локальный `git merge --squash feature` только готовит индекс и рабочее дерево.
Затем нужен `git commit`.
Не обходите GitHub-проверки локальным merge и прямым push в защищённую base.

Справочный CLI-фрагмент, **внешнее изменение, не выполнялся**:

```text
gh pr merge 123 --squash
```

До запуска проверьте условия:

- [ ] Выбран нужный PR.
- [ ] Окончательный diff проверен.
- [ ] Слияние разрешено.

При merge queue используйте предусмотренный репозиторием процесс очереди.

## Проверить результат и удалить ненужную ветку

После merge проверьте состояние PR.
Если применимо, проверьте результат деплоя.
Затем можно обновить main.
Ниже приведены отдельные справочные операции.
Remote delete меняет общий репозиторий.

```text
git switch main
git pull --ff-only
git branch --merged main
git branch -d feature/profile
git push origin --delete feature/profile
git fetch --prune origin
```

`branch -d` проверяет слитость по Git-истории.
После squash проверка не всегда проходит.
Если `branch -d` отказался, изучите `git log main..feature/profile`.
Изучите diff.
Изучите итог PR.
Принудительное локальное `-D` допустимо только после осознанной проверки сохранности работы.
Исчезнувший remote/upstream (`gone`) не доказывает, что локальная ветка больше не нужна.

## Разобраться с неправильным списком коммитов

Проверьте base и head.
Проверьте репозитории base и head.
Затем изучите `git log --oneline --graph --all` и merge-base.
После `fetch` выполните `git rev-list --left-right --count origin/main...HEAD`.
Команда показывает текущие ahead/behind локально.
Слева указаны коммиты только base.
Справа указаны коммиты только head.
История переписанной ветки автоматически отражается в PR.
Старые комментарии могут стать outdated.
Если после force push содержимое неожиданно изменилось, сохраните ссылки на нужные коммиты.
До повторной перезаписи выясните причину изменения.
[Reflog](../git/history.md) помогает изучить локальные прежние состояния.

## Источники и границы проверки

[Merge methods](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/configuring-pull-request-merges/about-merge-methods-on-github),
[CLI merge](https://cli.github.com/manual/gh_pr_merge), [git merge](https://git-scm.com/docs/git-merge),
[git branch](https://git-scm.com/docs/git-branch).
Сверка: 2026-11-06.
Слияния и удаления веток на GitHub не выполнялись.
Синтетические Git-сценарии находятся [в теме Git](../git/README.md).
