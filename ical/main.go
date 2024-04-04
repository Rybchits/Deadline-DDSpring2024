package main

import (
	"encoding/json"
	"errors"
	"fmt"
	ics "github.com/arran4/golang-ical"
	"io"
	"log"
	"net/http"
	"os"
	"strconv"
	"time"
)

const (
	fileServerIP   = "178.154.202.11"
	fileServerPort = "8888"
)

type icalReq struct {
	Name  string `json:"name"`
	Type  string `json:"type"`
	Tasks []struct {
		ID          int    `json:"id"`
		Title       string `json:"title"`
		Start       string `json:"start"`
		End         string `json:"end"`
		Description string `json:"description"`
	} `json:"tasks"`
}

type errBadTimeFormat struct {
	badFormat string
}

func (e errBadTimeFormat) Error() string {
	return fmt.Sprintf("bad time format: %s", e.badFormat)
}

func main() {
	http.Handle("/ical", http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		defer func() {
			if err := recover(); err != nil {
				w.WriteHeader(http.StatusInternalServerError)
				w.Write([]byte("internal server error"))
			}
		}()

		body, err := io.ReadAll(r.Body)
		if err != nil {
			w.WriteHeader(http.StatusBadRequest)
			w.Write([]byte(err.Error()))
			return
		}

		icalReq := icalReq{}
		err = json.Unmarshal(body, &icalReq)
		if err != nil {
			w.WriteHeader(http.StatusBadRequest)
			w.Write([]byte(err.Error()))
			return
		}

		path, err := makeCalendar(icalReq)
		if err != nil {
			status := http.StatusInternalServerError
			var errBadTimeFormat errBadTimeFormat
			if errors.As(err, &errBadTimeFormat) {
				status = http.StatusBadRequest
			}
			w.WriteHeader(status)
			w.Write([]byte(err.Error()))
			return
		}

		w.WriteHeader(http.StatusOK)
		w.Write([]byte(path))
	}))

	err := http.ListenAndServe(":8082", nil)
	if err != nil {
		log.Fatalf("Error starting server: %s", err)
	}
}

func makeCalendar(r icalReq) (string, error) {
	cal := ics.NewCalendar()
	cal.SetMethod(ics.MethodPublish)
	cal.AddTimezone("MSK")

	for _, task := range r.Tasks {
		e := cal.AddEvent(strconv.Itoa(task.ID))
		start, err := time.Parse("2006-01-02", task.Start)
		if err != nil {
			return "", errBadTimeFormat{badFormat: task.Start}
		}
		end, err := time.Parse("2006-01-02", task.End)
		if err != nil {
			return "", errBadTimeFormat{badFormat: task.End}
		}
		e.SetCreatedTime(start)
		e.SetStartAt(start)
		e.SetModifiedAt(time.Now())
		e.SetEndAt(end.Local())
		e.SetSummary(task.Title)
		e.SetDescription(task.Description)
	}
	out := cal.Serialize()

	var folder string
	switch r.Type {
	case "tag":
		folder = "tags"
	default:
		folder = "users"
	}

	path := fmt.Sprintf("./calendars/%s/%s.ics", folder, r.Name)
	f, err := os.OpenFile(path, os.O_RDWR|os.O_CREATE|os.O_TRUNC, 0666)
	if err != nil {
		return "", err
	}
	defer f.Close()
	f.Write([]byte(out))

	return fmt.Sprintf("http://%s:%s/%s/%s.ics", fileServerIP, fileServerPort, folder, r.Name), nil
}
