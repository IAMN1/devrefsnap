# Язык, модуль и ошибки

[Справочник Go](README.md) · [Конкурентность](concurrency-and-testing.md) · [HTTP](http-json.md)

**Уровень:** базовый → средний. Предпосылки: функции и коллекции. Сверено 2026-11-06 с Go 1.27. Выполнено 2026-11-06 на go1.27.1 darwin/arm64: demo выдал ожидаемый вывод; языковые тесты, gofmt, vet и race-прогон успешны. Все блоки с именами файлов образуют **один** стандартный модуль; сохраняй относительные пути после `go/`.

## Основные конструкции

| Задача | Конструкция и ограничение |
| --- | --- |
| Нулевое значение | `0`, `false`, `""`; slices/maps/pointers/channels/interfaces могут быть nil |
| Массив / срез | `[3]int{1, 2, 3}` / `[]int{1, 2, 3}`; длина массива входит в тип |
| Создание map | `make(map[string]int)`; чтение отсутствующего ключа возвращает zero value |
| Проверка ключа | `value, ok := counts["python"]`; `ok` отличает отсутствующий ключ от нуля |
| Указатель | `p := &user`, `*p`; арифметики указателей в обычном Go нет |
| Цикл | `for i := 0; i < n; i++`; `for condition`; `for key, value := range data` |
| Условие с инициализацией | `if value, ok := m[key]; ok { ... }` — синтаксический фрагмент |
| Функция как значение | `func(string) string`; замыкание может захватывать изменяемые данные |
| Константы | `const`, при необходимости `iota` для последовательностей |
| Пропуск значения | `_`; не используй его для молчаливого игнорирования важной ошибки |

Это фрагменты синтаксиса, не отдельная программа. `panic/recover` не заменяют обычный возврат `error`; recover срабатывает в отложенной функции соответствующей goroutine. В современном Go переменные `range`, объявленные через `:=`, создаются отдельно на итерацию; это не устраняет гонки на общих объектах.

## Полный модуль

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

Метод `String` с value receiver позволяет `User` удовлетворять `fmt.Stringer`. `Rename` с pointer receiver меняет исходный объект; он предполагает ненулевой указатель. `Clone` копирует элементы среза, но не делает глубокую копию объектов, на которые они ссылаются. Generic `comparable` разрешает сравнение `==`; `any` не даёт права выполнять произвольные операции над T.

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

`go run ./cmd/demo` выводит `Alice Doe (30)` и `true`. `log.Fatal` вызывает `os.Exit(1)`: отложенные функции при таком завершении не выполняются. В библиотечной функции возвращай ошибку вызывающему коду.

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

Проверка: `go test ./...`, затем `go vet ./...`. `fmt.Errorf("...: %w", err)` сохраняет цепочку причин; `%v` только форматирует текст. Не сравнивай текст ошибок как стабильный контракт, если нужен тип или причина. Numeric parsing проверяет формат и диапазон int текущей архитектуры; для сериализуемых идентификаторов при необходимости выбирай явный `int64` и соответствующий parser.

Источники: [спецификация](https://go.dev/ref/spec), [создание модуля](https://go.dev/doc/tutorial/create-module), [generics](https://go.dev/doc/tutorial/generics), [errors](https://pkg.go.dev/errors), [strconv](https://pkg.go.dev/strconv).
