package main

import (
	"log"
	"net/http"
)

func main() {
	fileServer := http.FileServer(http.Dir("./calendars"))

	http.Handle("/", http.StripPrefix("/", fileServer))

	err := http.ListenAndServe(":8083", nil)
	if err != nil {
		log.Fatalf("Error starting server: %s", err)
	}
}
