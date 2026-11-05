# Проверить JSON HTTP-запрос

[Справочник Go](README.md) · [Модуль](language.md#полный-модуль)

**Уровень:** средний → продвинутый. Предпосылки: HTTP, структуры, error. Сверено 2026-11-06 с `encoding/json`, `net/http`, `httptest` Go 1.27. Выполнено 2026-11-06 на go1.27.1 darwin/arm64: valid/invalid JSON, method/media type и body limit через Recorder; `go test`, vet и race-прогон успешны. Пример использует тот же модуль и стандартную библиотеку, без TCP-сервера и внешних запросов.

## Handler с границами ввода

Полный `http.go`: POST `/normalize` принимает имя, обрезает пробелы и возвращает JSON. Это обработка ввода, не регистрация и не сохранение в БД. Лимит 1 KiB выбран только для учебного payload.

<!-- example: go/http.go -->
```go
package cheatsheet

import (
	"encoding/json"
	"errors"
	"io"
	"log"
	"mime"
	"net/http"
	"strings"
)

const maxBodyBytes int64 = 1024

type namePayload struct {
	Name string `json:"name"`
}

func NewHandler() http.Handler {
	mux := http.NewServeMux()
	mux.HandleFunc("POST /normalize", normalizeName)
	return mux
}

func decodeError(w http.ResponseWriter, err error) {
	var limit *http.MaxBytesError
	if errors.As(err, &limit) {
		http.Error(w, "body too large", http.StatusRequestEntityTooLarge)
		return
	}
	http.Error(w, "invalid JSON", http.StatusBadRequest)
}

func normalizeName(w http.ResponseWriter, r *http.Request) {
	mediaType, _, err := mime.ParseMediaType(r.Header.Get("Content-Type"))
	if err != nil || mediaType != "application/json" {
		http.Error(w, "expected application/json", http.StatusUnsupportedMediaType)
		return
	}
	r.Body = http.MaxBytesReader(w, r.Body, maxBodyBytes)
	decoder := json.NewDecoder(r.Body)
	decoder.DisallowUnknownFields()
	var payload namePayload
	if err := decoder.Decode(&payload); err != nil {
		decodeError(w, err)
		return
	}
	if err := decoder.Decode(new(any)); err != io.EOF {
		if err == nil {
			http.Error(w, "one JSON value required", http.StatusBadRequest)
		} else {
			decodeError(w, err)
		}
		return
	}
	payload.Name = strings.TrimSpace(payload.Name)
	if payload.Name == "" {
		http.Error(w, "name required", http.StatusUnprocessableEntity)
		return
	}
	w.Header().Set("Content-Type", "application/json")
	if err := json.NewEncoder(w).Encode(payload); err != nil {
		log.Printf("encode normalization response: %v", err)
	}
}
```

JSON syntax, число JSON-значений и бизнес-правило имени проверяются отдельно. `DisallowUnknownFields` запрещает неизвестные поля, но не дубликаты ключей и не все особенности сопоставления регистра `encoding/json`; при таком контракте нужна дополнительная проверка. Ошибка записи ответа обрабатывается после начала отправки: сменить уже отправленный статус нельзя.

## Тест без сетевого сервера

Полный `http_test.go`:

<!-- example: go/http_test.go -->
```go
package cheatsheet

import (
	"encoding/json"
	"net/http"
	"net/http/httptest"
	"strings"
	"testing"
)

func TestJSONHandler(t *testing.T) {
	for _, tc := range []struct {
		name, body string
		want       int
	}{
		{"valid", `{"name":" Alice "}`, 200},
		{"empty-name", `{"name":" "}`, 422},
		{"malformed", `{"name":`, 400},
		{"unknown-field", `{"name":"Alice","extra":1}`, 400},
		{"wrong-type", `{"name":123}`, 400},
		{"trailing-value", `{"name":"Alice"}{"name":"Bob"}`, 400},
		{"oversized", `{"name":"` + strings.Repeat("x", 2048) + `"}`, 413},
	} {
		t.Run(tc.name, func(t *testing.T) {
			request := httptest.NewRequest(http.MethodPost, "/normalize", strings.NewReader(tc.body))
			request.Header.Set("Content-Type", "application/json")
			recorder := httptest.NewRecorder()
			NewHandler().ServeHTTP(recorder, request)
			if recorder.Code != tc.want {
				t.Fatalf("status = %d, want %d; body=%q", recorder.Code, tc.want, recorder.Body.String())
			}
			if tc.want == 200 {
				var payload namePayload
				if err := json.Unmarshal(recorder.Body.Bytes(), &payload); err != nil {
					t.Fatal(err)
				}
				if payload.Name != "Alice" || recorder.Header().Get("Content-Type") != "application/json" {
					t.Fatalf("response = %+v", payload)
				}
			}
		})
	}
}

func TestMethodAndMediaType(t *testing.T) {
	request := httptest.NewRequest(http.MethodGet, "/normalize", nil)
	recorder := httptest.NewRecorder()
	NewHandler().ServeHTTP(recorder, request)
	if recorder.Code != http.StatusMethodNotAllowed {
		t.Fatalf("GET status = %d", recorder.Code)
	}
	request = httptest.NewRequest(http.MethodPost, "/normalize", strings.NewReader(`{"name":"Alice"}`))
	recorder = httptest.NewRecorder()
	NewHandler().ServeHTTP(recorder, request)
	if recorder.Code != http.StatusUnsupportedMediaType {
		t.Fatalf("media type status = %d", recorder.Code)
	}
}
```

Запуск: `go test ./...`. Ожидаются нормализация имени и отдельные отказы 400/405/413/415/422. Recorder проверяет handler внутри процесса, не поднимая порт.

## Перед настоящим HTTP-запуском

| Задача | Что настроить |
| --- | --- |
| Принимать внешние запросы | `http.Server` с осмысленными `ReadHeaderTimeout`, `IdleTimeout` и политикой body/deadline; значения зависят от streaming и клиентов |
| Ограничить JSON | Лимит тела + лимиты структуры/числа элементов по требованиям; размер сам по себе не описывает всю стоимость обработки |
| Делать исходящие запросы | Переиспользуемый `http.Client` с timeout, `NewRequestWithContext`, закрытие `response.Body`, ограниченное чтение |
| Остановить сервер | `Server.Shutdown` с ограниченным context; отдельно управляй фоновыми задачами |
| Проверить эксплуатацию | TLS, proxy, нагрузки, закрытие соединений и отмену запросов проверяй отдельными сценариями |

Реальный сервер, TLS и нагрузочные сценарии этой страницей не запускались. Это таблица решений для следующей задачи, а не псевдокод готового production-сервера.

Источники: [encoding/json](https://pkg.go.dev/encoding/json), [net/http](https://pkg.go.dev/net/http), [httptest](https://pkg.go.dev/net/http/httptest), [context](https://pkg.go.dev/context).
