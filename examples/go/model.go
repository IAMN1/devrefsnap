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
