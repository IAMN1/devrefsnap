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
