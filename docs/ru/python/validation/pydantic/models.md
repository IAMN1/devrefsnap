
# Проверить модель и сериализовать данные

[English](../../../../en/python/validation/pydantic/models.md)

Откройте страницу, чтобы проверить входные данные, согласовать поля и сформировать публичный JSON.
Полные файлы дополняют [карточки Pydantic](README.md).

| Задача | Приём | Пример / подробности |
| --- | --- | --- |
| Проверить словарь и вывести JSON | `BaseModel`, aliases, validators | [Модели и тесты](#модели-валидация-и-json) |
| Скрыть пароль в публичном выводе | Отдельная выходная модель | [UserInput и PublicUser](#модели-валидация-и-json) |
| Читать атрибуты и ограничить типы | `from_attributes`, strict, frozen | [Типы и тесты](#атрибуты-конфигурация-и-типы) |

[Справочник](README.md) · [Расширенные задачи](advanced.md)

**Уровень:** базовый → средний.
**Предпосылки:** классы, типы, Decimal и JSON.
Поместите все файлы ниже в одну учебную папку.
Используйте Python 3.14.
Выполните `python -m pip install 'pydantic[email]==2.14.4' 'email-validator==2.4.0' 'pytest==9.2.0'`.


## Модели, валидация и JSON

Полный пример `demo_models.py` разделяет вход пользователя и публичный вывод.
Пример не возвращает пароль.

[`pydantic/demo_models.py`](../../../../../examples/python/validation/pydantic/demo_models.py)

Запустите `python demo_models.py`.
Результат содержит JSON пользователя без пароля.
У товара `final_price` равна `"0"`.
`model_dump()` сохраняет Decimal.
Параметр `mode="json"` делает строковое представление JSON-совместимым.
Для выборочного вывода используйте `include`, `exclude`, `exclude_unset` или `exclude_none`.
Эти параметры не меняют правила входа.
Сериализация с исключёнными обязательными полями не обязана проходить обратную проверку той же входной моделью.

Поле `created_at` требует timezone через `AwareDatetime`.
Модель отвергает значение без смещения.
Значение `2026-11-06T12:00:00+03:00` сериализуется как `2026-11-06T09:00:00Z`.
Преобразование не использует локальную timezone машины.
Вывод имеет точность до секунды.

Полный `test_models.py`:

[`pydantic/test_models.py`](../../../../../examples/python/validation/pydantic/test_models.py)


## Атрибуты, конфигурация и типы

Полный пример `demo_types.py` читает ORM-подобные объекты без подключения БД.
Для настоящего SQLAlchemy используйте [его рецепты](../../databases/sqlalchemy/README.md).

[`pydantic/demo_types.py`](../../../../../examples/python/validation/pydantic/demo_types.py)

Полный `test_types.py`:

[`pydantic/test_types.py`](../../../../../examples/python/validation/pydantic/test_types.py)

Запустите все тесты страницы: `python -m pytest -q test_models.py test_types.py`.
Ожидается успешная проверка допустимых значений.
Для указанных невалидных значений ожидаются отказы.
Телефон можно ограничить `Field(pattern=r'^\+?[1-9][0-9]{1,14}$')`.
Этот синтаксический шаблон не подтверждает существование номера.
После установки `pydantic-extra-types` импортируйте `PaymentCardNumber` для новых примеров из `pydantic_extra_types.payment`.
Не логируйте платёжные данные ради проверки типа.

Источники: [валидаторы](https://pydantic.dev/docs/validation/latest/concepts/validators/), [сериализаторы](https://pydantic.dev/docs/validation/latest/concepts/serialization/), [ConfigDict](https://pydantic.dev/docs/validation/latest/api/pydantic/config/), [стандартные типы](https://pydantic.dev/docs/validation/latest/api/pydantic/standard_library_types/), [PaymentCardNumber](https://pydantic.dev/docs/validation/latest/api/pydantic-extra-types/pydantic_extra_types_payment/).
