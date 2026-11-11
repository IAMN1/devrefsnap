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
