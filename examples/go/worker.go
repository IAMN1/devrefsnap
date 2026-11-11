package cheatsheet

import (
	"context"
	"errors"
	"strings"
	"sync"
)

var ErrWorkers = errors.New("workers must be positive")

func Uppercase(ctx context.Context, input []string, workers int) ([]string, error) {
	if workers < 1 {
		return nil, ErrWorkers
	}
	if err := ctx.Err(); err != nil {
		return nil, err
	}
	if workers > len(input) {
		workers = len(input)
	}
	type job struct {
		index int
		value string
	}
	jobs := make(chan job)
	result := make([]string, len(input))
	var group sync.WaitGroup
	group.Add(workers)
	for range workers {
		go func() {
			defer group.Done()
			for {
				select {
				case <-ctx.Done():
					return
				case task, ok := <-jobs:
					if !ok {
						return
					}
					result[task.index] = strings.ToUpper(task.value)
				}
			}
		}()
	}
sendLoop:
	for index, value := range input {
		select {
		case <-ctx.Done():
			break sendLoop
		case jobs <- job{index: index, value: value}:
		}
	}
	close(jobs)
	group.Wait()
	if err := ctx.Err(); err != nil {
		return nil, err
	}
	return result, nil
}
