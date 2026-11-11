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
