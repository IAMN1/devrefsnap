package main

import (
	"context"
	"errors"
	"fmt"
	"io"
	"net/http"
	"net/http/httptest"
	"os"
	"time"
)

func get(ctx context.Context, client *http.Client, url string) (string, error) {
	req, err := http.NewRequestWithContext(ctx, http.MethodGet, url, nil)
	if err != nil {
		return "", err
	}
	resp, err := client.Do(req)
	if err != nil {
		return "", err
	}
	defer resp.Body.Close()
	if resp.StatusCode != http.StatusOK {
		return "", fmt.Errorf("unexpected HTTP status: %s", resp.Status)
	}
	body, err := io.ReadAll(resp.Body)
	return string(body), err
}

func run() error {
	cancelStarted := make(chan struct{})
	mux := http.NewServeMux()
	mux.HandleFunc("/ok", func(w http.ResponseWriter, _ *http.Request) {
		_, _ = io.WriteString(w, "ok")
	})
	mux.HandleFunc("/timeout", func(_ http.ResponseWriter, r *http.Request) {
		<-r.Context().Done()
	})
	mux.HandleFunc("/cancel", func(_ http.ResponseWriter, r *http.Request) {
		close(cancelStarted) // This demo sends one request to /cancel.
		<-r.Context().Done()
	})
	server := httptest.NewServer(mux)
	defer server.Close()
	client := server.Client()

	parent, cancelAll := context.WithTimeout(context.Background(), 5*time.Second)
	defer cancelAll()

	body, err := get(parent, client, server.URL+"/ok")
	if err != nil {
		return fmt.Errorf("success request: %w", err)
	}
	if body != "ok" {
		return fmt.Errorf("unexpected body: %q", body)
	}
	fmt.Println("success:", body)

	deadlineCtx, stopTimer := context.WithTimeout(parent, 200*time.Millisecond)
	defer stopTimer()
	if _, err := get(deadlineCtx, client, server.URL+"/timeout"); !errors.Is(err, context.DeadlineExceeded) {
		return fmt.Errorf("expected DeadlineExceeded, got %v", err)
	}
	fmt.Println("timeout: context deadline exceeded")

	requestCtx, cancelRequest := context.WithCancel(parent)
	defer cancelRequest()
	go func() {
		select {
		case <-cancelStarted:
			cancelRequest()
		case <-requestCtx.Done():
		}
	}()
	if _, err := get(requestCtx, client, server.URL+"/cancel"); !errors.Is(err, context.Canceled) {
		return fmt.Errorf("expected Canceled, got %v", err)
	}
	fmt.Println("cancel: context canceled")
	return nil
}

func main() {
	if err := run(); err != nil {
		fmt.Fprintln(os.Stderr, err)
		os.Exit(1)
	}
}
