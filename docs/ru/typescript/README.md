# TypeScript

[Каталог](../README.md) · [English](../../en/typescript/README.md)

Выполните запрос `GET /` к локальному API из Node.js. Используйте TypeScript для проверки типов в коде и проверьте данные сервера во время выполнения.

| Задача | Приём |
| --- | --- |
| Проверить типы до запуска API | [`tsc --noEmit`](#проверить-типы-без-сервера) |
| Проверить данные из сети | [`response.ok`, `unknown` и проверка поля](#прочитать-и-проверить-json-ответ) |
| Отправить запрос и увидеть ответ | [Запуск сервера и клиента](#запустить-клиент) |

## Проверить типы без сервера

Из корня репозитория проверьте [клиент](../../../examples/typescript/http-client/client.mts) с помощью Node.js 26 и npm. При первом запуске npm скачает TypeScript 6.0.3, если пакета ещё нет в кэше.

```bash
npm exec --yes --package=typescript@6.0.3 -- tsc \
  --ignoreConfig --strict --noEmit --target ES2022 --module NodeNext \
  --lib ES2022,DOM examples/typescript/http-client/client.mts
```

При успешной проверке компилятор завершается с кодом 0 без вывода. Чтобы увидеть ошибку в учебной копии, замените `return { message: data.message }` на `return { message: 42 }`. Повторите команду. Компилятор сообщит, что `number` нельзя присвоить полю типа `string`. Верните исходную строку перед запуском клиента.

## Прочитать и проверить JSON-ответ

Клиент ожидает объект со строковым полем `message`. Тип `Greeting` описывает значение, которое вы получите после `await getGreeting(url)`.

```typescript
type Greeting = { message: string };
```

Фрагмент `getGreeting`. Параметр `url` содержит адрес API.

```typescript
const response = await fetch(url);
if (!response.ok) {
  throw new Error(`HTTP ${response.status}`);
}
const data: unknown = await response.json();
if (
  typeof data !== "object" ||
  data === null ||
  !("message" in data) ||
  typeof data.message !== "string"
) {
  throw new Error("Expected a JSON object with a string message");
}
```

`response.ok` принимает значение `true` при статусах от 200 до 299. Проверяйте статус до чтения JSON. Метод `response.json()` разбирает тело ответа. Тип `unknown` требует уточнить тип значения перед обращением к его полям. После блока `if` компилятор знает, что `data.message` — строка.

## Запустить клиент

Используйте Node.js 26 с npm и Python 3.14. Команда компиляции использует TypeScript 6.0.3 из кэша npm. Если пакета нет в кэше, npm загрузит пакет. Клиент использует встроенный `fetch` в Node.js.

В первом терминале запустите [минимальный API FastAPI](../../../examples/python/web/fastapi/minimal.py) из корня репозитория. Порт `8000` должен быть свободен.

```bash
api_env=$(mktemp -d)
python3.14 -m venv "$api_env"
"$api_env/bin/python" -m pip install 'fastapi==0.162.0' 'uvicorn==0.54.0'
"$api_env/bin/python" -m uvicorn minimal:app --app-dir examples/python/web/fastapi --host 127.0.0.1 --port 8000
```

Во втором терминале из корня репозитория скомпилируйте [полный клиент `client.mts`](../../../examples/typescript/http-client/client.mts). Запустите полученный файл `client.mjs`.

```bash
cd examples/typescript/http-client
client_dir=$(mktemp -d)
npm exec --yes --package=typescript@6.0.3 -- tsc \
  --ignoreConfig --strict --noEmitOnError --target ES2022 --module NodeNext \
  --lib ES2022,DOM --outDir "$client_dir" client.mts
node "$client_dir/client.mjs"
```

`--ignoreConfig` позволяет скомпилировать указанный файл независимо от `tsconfig.json`. `--strict` включает строгую проверку типов. `--noEmitOnError` запрещает создавать JavaScript при ошибке компиляции. Библиотека типов `DOM` даёт компилятору объявления `fetch` и `Response`. Расширение `.mjs` обозначает модуль JavaScript и позволяет использовать `await` на верхнем уровне.

При успешном ответе клиент выведет `Привет`. При ответе `404` клиент завершится с ошибкой `HTTP 404`. Если в успешном JSON-ответе поле `message` содержит число, клиент завершится с ошибкой `Expected a JSON object with a string message`.

Остановите сервер через `Ctrl+C` в первом терминале. Временные каталоги находятся по путям `$api_env` и `$client_dir`.

В [сквозном примере](../tools/api-contract-lab.md) такой клиент проверяет два ответа FastAPI с PostgreSQL локально и в CI.

## Источники

- [TypeScript Handbook о сужении типов](https://www.typescriptlang.org/docs/handbook/2/narrowing.html).
- [Параметры `tsc`](https://www.typescriptlang.org/docs/handbook/compiler-options.html), [TypeScript 6.0 о `--ignoreConfig`](https://www.typescriptlang.org/docs/handbook/release-notes/typescript-6-0.html#specifying-command-line-files-when-tsconfigjson-exists-is-now-an-error) и [TypeScript 4.7 о `.mts` и `.mjs`](https://www.typescriptlang.org/docs/handbook/release-notes/typescript-4-7.html#new-file-extensions).
- [Node.js 26.8.2 о `fetch`](https://nodejs.org/download/release/v26.8.2/docs/api/globals.html#fetch), [спецификация Fetch о `Response.ok`](https://fetch.spec.whatwg.org/#dom-response-ok) и [документация `npm exec`](https://docs.npmjs.com/cli/v11/commands/npm-exec/).
