
# Проверить структуры и TTL Redis

[English](../../../../en/databases/non-relational/redis/data-lab.md)

Откройте страницу для полного запуска операций со строкой, профилем, очередью, тегами и рейтингом.
Используйте отдельный Redis 8.2 с синтетическими данными.
[К карточкам данных и кеша](data-and-caching.md) · [К Redis](README.md).

Нужны Redis 8.2, Python 3.14 и redis-py 8.1.0.


## Подготовка

Установите клиент в отдельное временное/учебное окружение: `python -m pip install 'redis==8.1.0'`.
Сначала подготовьте [изолированный Redis](operations.md#учебный-экземпляр).
Проверьте адрес Redis.
Задайте REDIS_URL.
Для собственного Unix socket используйте форму `export REDIS_URL='unix:///путь/redis.sock?db=0'`.
Для выделенного TCP-экземпляра используйте форму `redis://127.0.0.1:порт/0`.
Не направляйте примеры в рабочую БД.


## Полный пример: структуры и TTL

Сохраните пример как `data.py`.
Выполните `python data.py`.
Все ключи получают уникальный namespace.
Блок finally удаляет только созданные ключи при успешном запуске и при ошибке.

[`redis/data.py`](../../../../../examples/databases/non-relational/redis/data.py)

**Результат:** пример выводит строку OK без исключений.
Проверки оценивают корректность операций, а не скорость или точность таймера.
List с LPOP выше показывает порядок.
Этот list не реализует надёжную очередь задач.
После извлечения нет ACK или повторной доставки.
Для такого протокола нужен другой дизайн, например [stream](transactions-and-messaging.md#полный-пример-stream-и-pubsub).


## Источники

- [Структуры](https://redis.io/docs/latest/develop/data-types/), [SET](https://redis.io/docs/latest/commands/set/), [EXPIRE](https://redis.io/docs/latest/commands/expire/), [TTL](https://redis.io/docs/latest/commands/ttl/).
- [SCAN](https://redis.io/docs/latest/commands/scan/), [eviction](https://redis.io/docs/latest/develop/reference/eviction/), [cache-aside](https://redis.io/tutorials/howtos/solutions/microservices/caching/).
- [Redis 8.2.11: release notes](https://github.com/redis/redis/releases/tag/8.2.11).
