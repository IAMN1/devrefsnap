# Полный модуль: язык и ошибки

Откройте страницу, чтобы собрать полный код после [коротких карточек](../language.md).

| Задача | Приём | Пример |
| --- | --- | --- |
| Создать и запустить модуль | `go.mod + модель + main` | [Полный модуль](#полный-модуль) |
| Проверить ввод и сохранность объекта | `Тесты NewUser и Rename` | [Тесты](#проверка-валидного-и-невалидного-ввода) |

[Справочник Go](../README.md) · [Конкурентность](../concurrency-and-testing.md) · [HTTP](../http-json.md)

## Подготовка

Предпосылки: функции и коллекции.
Для запуска нужен Go 1.27.
Создайте отдельный учебный каталог.
Сохраните в нём файлы этой страницы.
Все блоки с именами файлов образуют один модуль без сторонних зависимостей.
Сохраняйте относительные пути после `go/`.

Основные конструкции и ограничения `range` смотрите [в кратком справочнике](../language.md#основные-конструкции).

## Полный модуль

<a id="go-mod"></a>

Файл `go.mod`:

<!-- example: go/go.mod -->
```text
module example.com/cheatsheet

go 1.27.0
```

Полный `model.go`:

<!-- example: go/model.go -->
```go
package cheatsheet

import (
	"errors"
	"fmt"
	"strconv"
	"strings"
)

var ErrEmptyName = errors.New("empty name")
var ErrInvalidAge = errors.New("negative age")

type User struct {
	Name string `json:"name"`
	Age  int    `json:"age"`
}

func NewUser(name, ageText string) (User, error) {
	name = strings.TrimSpace(name)
	if name == "" {
		return User{}, fmt.Errorf("create user: %w", ErrEmptyName)
	}
	age, err := strconv.Atoi(ageText)
	if err != nil {
		return User{}, fmt.Errorf("parse age: %w", err)
	}
	if age < 0 {
		return User{}, fmt.Errorf("create user: %w", ErrInvalidAge)
	}
	return User{Name: name, Age: age}, nil
}

func (u User) String() string {
	return fmt.Sprintf("%s (%d)", u.Name, u.Age)
}

func (u *User) Rename(name string) error {
	name = strings.TrimSpace(name)
	if name == "" {
		return ErrEmptyName
	}
	u.Name = name
	return nil
}

var _ fmt.Stringer = User{}

func Describe(value fmt.Stringer) string {
	return value.String()
}

func Contains[T comparable](values []T, wanted T) bool {
	for _, value := range values {
		if value == wanted {
			return true
		}
	}
	return false
}

func Clone[T any](values []T) []T {
	return append([]T(nil), values...)
}

func Counts(values []string) map[string]int {
	counts := make(map[string]int)
	for _, value := range values {
		counts[value]++
	}
	return counts
}
```

Метод `String` с value receiver позволяет `User` удовлетворять `fmt.Stringer`.
Метод `Rename` с pointer receiver меняет исходный объект.
Метод `Rename` предполагает ненулевой указатель.
`Clone` копирует элементы среза.
`Clone` не создаёт глубокую копию объектов, на которые ссылаются элементы.
Ограничение `comparable` разрешает сравнение `==`.
Ограничение `any` не разрешает произвольные операции над T.

Полный `cmd/demo/main.go`:

<!-- example: go/cmd/demo/main.go -->
```go
package main

import (
	"fmt"
	"log"

	"example.com/cheatsheet"
)

func main() {
	user, err := cheatsheet.NewUser(" Alice ", "30")
	if err != nil {
		log.Fatal(err)
	}
	if err := user.Rename("Alice Doe"); err != nil {
		log.Fatal(err)
	}
	fmt.Println(cheatsheet.Describe(user))
	fmt.Println(cheatsheet.Contains([]string{"go", "python"}, "go"))
}
```

`go run ./cmd/demo` выводит `Alice Doe (30)` и `true`.
`log.Fatal` вызывает `os.Exit(1)`.
При таком завершении отложенные функции не выполняются.
В библиотечной функции возвращайте ошибку вызывающему коду.

## Проверка валидного и невалидного ввода

Полный `model_test.go`. Тесты входят в пакет и не требуют внешнего сервиса.

<!-- example: go/model_test.go -->
```go
package cheatsheet

import (
	"errors"
	"reflect"
	"strconv"
	"testing"
)

func TestUserAndInterfaces(t *testing.T) {
	user, err := NewUser(" Alice ", "30")
	if err != nil {
		t.Fatal(err)
	}
	if err := user.Rename("Alice Doe"); err != nil {
		t.Fatal(err)
	}
	if got := Describe(user); got != "Alice Doe (30)" {
		t.Fatalf("Describe = %q", got)
	}
	if err := user.Rename(" "); !errors.Is(err, ErrEmptyName) {
		t.Fatalf("Rename error = %v", err)
	}
	if user.Name != "Alice Doe" {
		t.Fatal("invalid rename changed user")
	}
}

func TestWrappedErrors(t *testing.T) {
	for _, tc := range []struct {
		name, age string
		want      error
	}{
		{" ", "30", ErrEmptyName},
		{"Alice", "-1", ErrInvalidAge},
	} {
		_, err := NewUser(tc.name, tc.age)
		if !errors.Is(err, tc.want) {
			t.Fatalf("error = %v, want cause %v", err, tc.want)
		}
	}
	_, err := NewUser("Alice", "not-a-number")
	var numberError *strconv.NumError
	if !errors.As(err, &numberError) {
		t.Fatalf("error has no NumError: %v", err)
	}
}

func TestCollectionsAndGenerics(t *testing.T) {
	original := []int{1, 2, 3}
	copied := Clone(original)
	copied[0] = 99
	if original[0] != 1 || !Contains(original, 2) || Contains(original, 9) {
		t.Fatal("clone or generic search failed")
	}
	counts := Counts([]string{"go", "go", "python"})
	if !reflect.DeepEqual(counts, map[string]int{"go": 2, "python": 1}) {
		t.Fatalf("counts = %v", counts)
	}
	if _, ok := counts["missing"]; ok {
		t.Fatal("missing key unexpectedly present")
	}
}
```

Запустите `go test ./...`.
Затем запустите `go vet ./...`.
`fmt.Errorf("...: %w", err)` сохраняет цепочку причин.
`%v` только форматирует текст.
Если нужен тип или причина ошибки, не используйте сравнение текста как стабильный контракт.
Разбор числа проверяет формат и диапазон int текущей архитектуры.
Для сериализуемых идентификаторов при необходимости выбирайте явный `int64` и соответствующий parser.

Источники: [спецификация](https://go.dev/ref/spec), [создание модуля](https://go.dev/doc/tutorial/create-module), [generics](https://go.dev/doc/tutorial/generics), [errors](https://pkg.go.dev/errors), [strconv](https://pkg.go.dev/strconv).
