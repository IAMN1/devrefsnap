# Структуры, TTL и кеширование

[К Redis](README.md)

| Параметр | Значение |
| --- | --- |
| Уровни | Базовый — структуры/TTL; средний — кеширование |
| Предпосылки | Выделенный Redis 8.2, Python 3.14 и redis-py 8.1.0 |
| Сверено с документацией | 2026-11-06 |
| Выполнено | 2026-11-06: полный пример на Redis 8.2.11 / redis-py 8.1.0 / Python 3.14.7, выделенный Unix socket; проверены структуры, INCR, KEEPTTL и истечение; ключи очищены |
| Не проверено | Прикладная cache-aside интеграция, нагрузка, eviction и отказы сервера |

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
finally удаляет только явно созданные ключи.
Пример очищает временные данные и при успешном запуске.

<!-- example: redis/data.py -->
```python
import os
import time
import uuid
from redis import Redis

client = Redis.from_url(os.environ["REDIS_URL"], decode_responses=True, socket_timeout=3)
prefix = f"cheatsheet:{{{uuid.uuid4().hex}}}:"
cache, counter, profile, tags, queue, ranking = [
    prefix + name for name in ("cache", "counter", "profile", "tags", "queue", "ranking")
]
keys = [cache, counter, profile, tags, queue, ranking]
try:
    assert client.ping()
    assert client.set(cache, '{"name":"Ada"}', ex=60, nx=True)
    assert 0 < client.ttl(cache) <= 60
    client.set(cache, '{"name":"Ada Lovelace"}', keepttl=True)
    assert 0 < client.ttl(cache) <= 60
    assert client.pexpire(cache, 0)
    assert client.ttl(cache) == -2
    client.set(cache, "temporary", px=40)
    time.sleep(0.08)
    assert client.get(cache) is None

    assert client.incrby(counter, 2) == 2
    client.hset(profile, mapping={"name": "Ada", "language": "Python"})
    assert client.hgetall(profile) == {"name": "Ada", "language": "Python"}
    client.sadd(tags, "sql", "python", "sql")
    assert client.smembers(tags) == {"sql", "python"}
    client.rpush(queue, "first", "second")
    assert client.lpop(queue) == "first"
    assert client.lrange(queue, 0, -1) == ["second"]
    client.zadd(ranking, {"Ada": 10, "Bob": 20})
    assert client.zrevrange(ranking, 0, 0, withscores=True) == [("Bob", 20.0)]
    print("OK: structures, atomic counter, TTL preservation and expiry")
finally:
    client.unlink(*keys)
    client.close()
```

**Результат:** пример выводит строку OK без исключений.
Пример удаляет только собственные ключи.
Проверки оценивают корректность.
Проверки не измеряют скорость или точность таймера.
List с LPOP выше показывает порядок.
Этот list не реализует надёжную очередь задач.
После извлечения нет ACK или повторной доставки.
Для такого протокола нужен другой дизайн, например [stream](transactions-and-messaging.md#полный-пример-stream-и-pubsub).

| Данные | Команды | Ограничение |
| --- | --- | --- |
| String / двоичное значение | SET/GET/MGET, INCR | INCR требует строковое целое; сериализацию объекта выбирает приложение |
| Hash | HSET/HGET/HGETALL | Отдельные поля; тип/валидацию полей определяет приложение |
| List | LPUSH/RPUSH/LPOP/LRANGE | Порядок элементов; большие диапазоны дорого передавать |
| Set | SADD/SISMEMBER/SINTER | Уникальность, порядок не гарантирован |
| Sorted set | ZADD/ZRANGE/ZREVRANGE | Сортировка по score, при равенстве — правила структуры |
| Bitmap / HyperLogLog / geo | SETBIT / PFADD / GEOADD | Специализированные задачи; HyperLogLog даёт оценку количества, не точное множество |
| Stream | XADD/XREADGROUP/XACK | Журнал сообщений и учёт доставки; сохраняемость зависит от конфигурации |

Проверьте тип через TYPE.
Повторное использование имени для другой структуры даёт WRONGTYPE.
TTL/PTTL возвращают секунды/миллисекунды.
EXPIRE/PEXPIRE меняют срок.
PERSIST снимает срок.
Замена значения SET обычно удаляет TTL.
INCR/HSET не заменяют весь ключ этим способом.
Для обхода большого namespace используйте SCAN с MATCH/COUNT.
Учитывайте возможные повторы и изменения во время обхода.
COUNT задаёт подсказку, а не жёсткий размер порции.

## Кеширование cache-aside

**Средний уровень.** Источник истины находится в основной БД.
Redis хранит копию с ограниченным сроком.

```mermaid
flowchart TD
    A[Запрос приложения] --> B{GET кеша}
    B -->|Есть| C[Вернуть кешированное значение]
    B -->|Нет| D[Прочитать основную БД]
    D --> E[SET значения с TTL]
    E --> F[Вернуть прочитанное значение]
    G[Изменение основной БД] --> H[Зафиксировать изменение]
    H --> I[Инвалидировать или обновить кеш]
```

Схема показывает протокол без гарантии строгой согласованности.
Конкурентное чтение может заполнить кеш старым значением после инвалидирования.
Выберите допустимую устарелость, версионирование или другой протокол.
Добавляйте небольшой разброс TTL, чтобы уменьшить массовое одновременное истечение.
Ограничивайте параллельное заполнение горячего ключа.
Для отсутствующих объектов можно кешировать специальный отрицательный ответ на короткий срок.

Ошибка кеша не должна молча перегрузить основную БД.
Задайте лимиты, наблюдение и определённый fallback.
Отдельно задайте maxmemory и eviction policy.
Кешируемые и незаменимые данные часто стоит разделить по экземплярам.
Цель разделения — сохранить прикладное состояние при вытеснении кеша.
SET NX PX может быть частью блокировки.
Безопасное освобождение блокировки требует проверки токена.
Без анализа отказов SET NX PX не образует готовую распределённую блокировку.

## Источники

- [Структуры](https://redis.io/docs/latest/develop/data-types/), [SET](https://redis.io/docs/latest/commands/set/), [EXPIRE](https://redis.io/docs/latest/commands/expire/), [TTL](https://redis.io/docs/latest/commands/ttl/).
- [SCAN](https://redis.io/docs/latest/commands/scan/), [eviction](https://redis.io/docs/latest/develop/reference/eviction/), [cache-aside](https://redis.io/tutorials/howtos/solutions/microservices/caching/).
