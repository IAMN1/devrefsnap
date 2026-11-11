# Участие в проекте / Contributing

[Русский](#русский) · [English](#english)

## Русский

Пишите заголовок и текст issue или pull request (PR) на русском или английском языке.

### Сообщить об ошибке или предложить тему

Откройте [список форм GitHub](https://github.com/IAMN1/Python_cheat_sheet/issues/new/choose).

- **Исправить или обновить материал.** Дайте ссылку на страницу и раздел. Опишите проблему и ожидаемый результат. Для ошибки в примере укажите версии, шаги и фактический вывод. Для обновления API приложите официальную документацию или примечания к выпуску нужной версии.
- **Предложить тему.** Опишите задачу читателя и результат, который он должен получить. Укажите ближайшую страницу из [каталога](docs/ru/README.md#каталог-материалов), если такая страница есть.

### Подготовить изменение

1. Откройте ссылку на другой язык в начале страницы. У парной страницы тот же путь после `docs/ru/` или `docs/en/`. Например, сопоставьте [русскую страницу о N+1](docs/ru/python/databases/sqlalchemy/n-plus-one.md) и [английскую страницу о N+1](docs/en/python/databases/sqlalchemy/n-plus-one.md).
2. Проверьте, относится ли правка к обеим версиям. Если парной странице нужна правка, внесите её или укажите в PR, какую часть ещё нужно обновить.
3. Правьте полный пример в [общем каталоге примеров](examples/README.md). Обе страницы должны ссылаться на один файл, например [n_plus_one.py](examples/python/databases/sqlalchemy/n_plus_one.py). Сверьте команды запуска и ожидаемый результат в обеих версиях.
4. Для новой темы выберите [шаблон по задаче](templates/README.md#выбор-формата). Добавьте ссылки в каталог языка, README раздела и указатель задач. Сохраните одинаковые пути и добавьте переходы между языковыми версиями.

### Проверить и отправить PR

1. Запустите [статические проверки материалов](scripts/README.md#запустить-локально). Они проверяют локальные ссылки, якоря, ограждения и синтаксис примеров.
2. Если изменили полный пример, выполните его в отдельном учебном окружении с указанными зависимостями. Для изменённой рекомендации сверяйтесь с официальной документацией нужной версии.
3. Напишите сообщение коммита на английском в формате Conventional Commits, например `docs: clarify SQLite transaction behavior`. Откройте PR в `main`.
4. Опишите, что изменилось для читателя. Укажите страницы, состояние парной версии и связанный issue, если он есть. Запишите команды, версии и результаты выполненных проверок. Укажите отдельно, что сверили с документацией и какие сценарии ещё требуют проверки.

## English

Write the title and body of an issue or pull request (PR) in either Russian or English.

### Report a problem or propose a topic

Open the [GitHub issue form chooser](https://github.com/IAMN1/Python_cheat_sheet/issues/new/choose).

- **Fix or update material.** Link to the page and section. Describe the problem and the expected result. For a broken example, include versions, steps, and actual output. For an API update, link to the official documentation or release notes for the relevant version.
- **Propose a topic.** Describe the reader's task and the result they should achieve. Link to the closest page in the [catalog](docs/en/README.md#material-catalog), if one exists.

### Prepare the change

1. Follow the language link near the top of the page. The matching page has the same path after `docs/en/` or `docs/ru/`. For example, compare the [English N+1 page](docs/en/python/databases/sqlalchemy/n-plus-one.md) and the [Russian N+1 page](docs/ru/python/databases/sqlalchemy/n-plus-one.md).
2. Check whether the change applies to both editions. If the matching page needs an update, make the update or describe what still needs work in the PR.
3. Edit the complete example in the [shared examples directory](examples/README.md). Both pages should link to the same file, such as [n_plus_one.py](examples/python/databases/sqlalchemy/n_plus_one.py). Check the run commands and expected output in both editions.
4. For a new topic, choose a [template by page purpose (Russian)](templates/README.md#выбор-формата). Link the page from the language catalog, section README, and task index. Use matching paths and link the language editions to each other.

### Verify and submit the PR

1. Run the commands under [local material checks (Russian)](scripts/README.md#запустить-локально). Use Python 3.13 on Linux x86_64 or Python 3.14 on macOS arm64. The checks cover local links, anchors, code fences, and example syntax.
2. If you changed a complete example, run it in a separate practice environment with the listed dependencies. For a changed recommendation, check the official documentation for the relevant version.
3. Write your commit message in English using Conventional Commits, for example `docs: clarify SQLite transaction behavior`. Open the PR against `main`.
4. Describe what changed for the reader. List the pages, the status of the matching edition, and the related issue, if any. Report the commands, versions, and results of the checks you ran. Identify what you checked against documentation and which scenarios still need verification.
