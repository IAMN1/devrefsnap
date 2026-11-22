# Проверка справочника с читателями

Проверьте, может ли читатель найти пример от задачи и объяснить полученный результат. Используйте один коммит для всех участников. Начните с [корневого README](../../README.md). Разрешите поиск по странице и переходы по ссылкам.

Показывайте задания по одному. При нескольких участниках меняйте порядок. Если человек застрял, запишите место остановки. Затем дайте минимальную подсказку и отдельно оцените объяснение результата.

## Задания на русском

1. Учебный API возвращает карточку товара. Найдите, как отправить запрос из терминала и увидеть код ответа и тип содержимого. Затем выведите только значение поля `name` и объясните вывод.
2. В учебном автоматическом запуске один тест специально настроили на отказ. Найдите нужный шаг в журнале. Назовите тест, фактическое и ожидаемое значения. Объясните, как получить успешный запуск.
3. Странице пользователей нужны все их посты, включая пустые списки. Число постов сильно различается. Сейчас чтение списка выполняет отдельный запрос для каждого пользователя. Ключ пользователя простой, несколько обращений к базе допустимы. Найдите подходящую загрузку и объясните её цену. Что изменится, если коллекции станут маленькими, а отдельное обращение к базе будет дорогим?
4. В проекте `main.py` лежит в корне, а Dockerfile в `dockers/`. Найдите, где исключить локальные файлы и как запустить проект с Compose в этом подкаталоге.

## Tasks in English

1. A practice API returns a product record. Find how to send a terminal request and see the response status and content type. Then print only the value of `name` and explain the output.
2. One test in a practice automated run was set up to fail on purpose. Find the relevant log step. Name the test and the actual and expected values. Explain how to get a passing run.
3. A users page needs every user's posts, including empty lists. Post counts vary widely. Reading the list currently runs a separate query for each user. Each user has a simple key, and several database round trips are acceptable. Find a loading approach and explain its cost. What changes if collections become small and an extra round trip is expensive?
4. Your project has a root-level `main.py` and a Dockerfile in `dockers/`. Find where to exclude local files and how to run the project with Compose in that subdirectory.

## Подготовка и критерии для ведущего

Для первого задания подготовьте локальную копию справочника на проверяемом коммите, два терминала, `python3`, `curl` и `jq`. Проверьте, что порт из [учебного примера](../../docs/ru/tools/http-json.md#запустить-учебный-сервер) свободен. Если вы запустили сервер заранее, отметьте это в форме.

Для второго задания используйте [архив завершённых учебных запусков в сохранённом коммите](https://github.com/IAMN1/devrefsnap/blob/2b164491a2c880fc69484d78c73c6ad777d8f2dd/maintenance/reports/github-actions-lab/README.md). После выбора рецепта дайте участнику ссылку на архив. Если проверяете только чтение фрагмента, покажите фрагмент после того, как участник назовёт задание и шаг. Запишите режим проверки в форме.

| Задание | Результат поиска и объяснения |
| --- | --- |
| HTTP | Читатель показывает код `200` и `Content-Type: application/json`, затем получает `Book` из тела. Он объясняет, почему обработчик JSON получает только тело. |
| CI | Читатель находит блок `Run python -m unittest -v` задания `integration`, тест `test_reports_current_database` и сравнение `compose_lab` с `intentional_failure`. Он выбирает новый запуск с выключенным параметром. |
| N+1 | Читатель выбирает `selectinload` для полных коллекций переменного размера и учитывает дополнительные пакетные SELECT. Для малых коллекций он сравнивает стоимость `joinedload` и учитывает повторение полей родителя и `unique()`. |
| Контекст Docker | Читатель находит [рабочий пример](../../docs/ru/tools/docker/build-context.md). Он указывает корневой `.dockerignore`, `context: ..` для вложенного файла Compose и ожидаемый вывод `/app/main.py`. |

Откройте [полный журнал запуска с отказом](https://github.com/IAMN1/devrefsnap/blob/2b164491a2c880fc69484d78c73c6ad777d8f2dd/maintenance/reports/github-actions-lab/43265099266.log). Найдите блок `Run python -m unittest -v`. Блок соответствует шагу `Run database test` в [манифесте](https://github.com/IAMN1/devrefsnap/blob/2b164491a2c880fc69484d78c73c6ad777d8f2dd/maintenance/reports/github-actions-lab/manifest.json). Архив сохраняет текст журнала; навигацию по интерфейсу GitHub Actions этот режим не проверяет. Для проверки по фрагменту используйте строки ниже.

```text
FAIL: test_reports_current_database (test_app.DatabaseStatusTest.test_reports_current_database)
AssertionError: 'compose_lab' != 'intentional_failure'
FAILED (failures=1)
```

## Запись наблюдений

Для участника достаточно условного идентификатора. Отдельно зафиксируйте язык, опыт, коммит, просмотрщик, ширину окна, начальную страницу и порядок заданий.

| Задание | Первый поиск или переход | Маршрут и возвраты | Время до рецепта | Выбранный фрагмент | Объяснение или ошибка | Подсказка и режим журнала |
| --- | --- | --- | --- | --- | --- | --- |
|  |  |  |  |  |  |  |

Сопоставьте наблюдения с [редакторским проходом](../reports/navigation-review.md#репетиция-трёх-читательских-задач).
