# Базы данных

[Найти пример по задаче или синониму](../tasks/README.md#базы-данных-и-sql) — SQL, ORM, PostgreSQL, SQLite и Redis.

Раздел описывает SQL и особенности конкретных СУБД.
Материалы охватывают запросы, структуру данных и работу с самой базой.
Библиотеки доступа к БД из Python находятся в [разделе Python](../python/README.md).
Один из материалов описывает [SQLAlchemy](../python/databases/sqlalchemy/README.md).

## Материалы

| Тема | Содержание |
| --- | --- |
| [SQL](sql/README.md) | Общие запросы и явно обозначенные различия диалектов |
| [PostgreSQL](relational/postgresql/README.md) | Запросы, эксплуатация и [проверка резервной копии](relational/postgresql/backup-and-restore.md) |
| [SQLite](relational/sqlite/README.md) | Встраиваемая СУБД, [копия и восстановление](relational/sqlite/backup-and-restore.md), миграции |
| [Redis](non-relational/redis/README.md) | Структуры данных, TTL, кэш и обмен сообщениями |

Общий SQL хранится отдельно от особенностей СУБД.
SQLite относится к реляционным базам.
Слово «встраиваемая» описывает способ работы SQLite.
Redis сгруппирован как нереляционное хранилище.

## Связанные темы

- [SQLAlchemy](../python/databases/sqlalchemy/README.md) — работа с СУБД из Python.
- [Проектирование Python-проекта](../python/architecture/project-design/README.md) — место слоя доступа к данным в приложении.

[Все материалы](../README.md)
