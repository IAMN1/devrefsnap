package cheatsheet

import (
	"context"
	"errors"
	"reflect"
	"sync"
	"testing"
	"time"
)

func TestUppercasePreservesOrder(t *testing.T) {
	ctx, cancel := context.WithTimeout(context.Background(), time.Second)
	defer cancel()
	got, err := Uppercase(ctx, []string{"go", "python", "rust"}, 2)
	if err != nil || !reflect.DeepEqual(got, []string{"GO", "PYTHON", "RUST"}) {
		t.Fatalf("Uppercase = %v, %v", got, err)
	}
	empty, err := Uppercase(ctx, nil, 2)
	if err != nil || len(empty) != 0 {
		t.Fatalf("empty input = %v, %v", empty, err)
	}
}

func TestUppercaseRejectsInvalidWorkersAndCancellation(t *testing.T) {
	if _, err := Uppercase(context.Background(), []string{"go"}, 0); !errors.Is(err, ErrWorkers) {
		t.Fatalf("workers error = %v", err)
	}
	ctx, cancel := context.WithCancel(context.Background())
	cancel()
	if _, err := Uppercase(ctx, []string{"go"}, 2); !errors.Is(err, context.Canceled) {
		t.Fatalf("cancellation error = %v", err)
	}
}

func TestCounterConcurrentUpdates(t *testing.T) {
	var counter Counter
	var group sync.WaitGroup
	for range 20 {
		group.Add(1)
		go func() {
			defer group.Done()
			for range 100 {
				counter.Add(1)
			}
		}()
	}
	group.Wait()
	if got := counter.Value(); got != 2000 {
		t.Fatalf("counter = %d, want 2000", got)
	}
}
