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
	Tasks []struct {
		ID          int    `json:"id"`
		Title       string `json:"title"`
		Start       string `json:"start"`
		End         string `json:"end"`
		Description string `json:"description"`
	} `json:"tasks"`
}

type errBadTimeFormat struct {
	format string
}

func (e errBadTimeFormat) Error() string {
	return fmt.Sprintf("bad time format: %s", e.format)
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

		err = makeCalendar(icalReq)
		if err != nil {
			status := http.StatusInternalServerError
			if errors.As(err, &errBadTimeFormat{}) {
				status = http.StatusBadRequest
			}
			w.WriteHeader(status)
			w.Write([]byte(err.Error()))
			return
		}

		w.WriteHeader(http.StatusOK)
	}))

	err := http.ListenAndServe(":8082", nil)
	if err != nil {
		log.Fatalf("Error starting server: %s", err)
	}
}

func makeCalendar(r icalReq) error {
	cal := ics.NewCalendar()
	cal.SetMethod(ics.MethodPublish)
	cal.AddTimezone("MSK")

	for _, task := range r.Tasks {
		e := cal.AddEvent(strconv.Itoa(task.ID))
		start, err := time.Parse("2006-01-02 15:04:05", task.Start)
		if err != nil {
			return errBadTimeFormat{format: task.Start}
		}
		end, err := time.Parse("2006-01-02 15:04:05", task.End)
		if err != nil {
			return errBadTimeFormat{format: task.End}
		}
		start = start.Add(-time.Hour * 3)
		end = end.Add(-time.Hour * 3)
		e.SetCreatedTime(start)
		e.SetStartAt(start)
		e.SetModifiedAt(time.Now())
		e.SetEndAt(end)
		e.SetSummary(task.Title)
		e.SetDescription(task.Description)
	}
	out := cal.Serialize()

	path := fmt.Sprintf("./calendars/%s.ics", r.Name)
	f, err := os.OpenFile(path, os.O_RDWR|os.O_CREATE|os.O_TRUNC, 0666)
	if err != nil {
		return err
	}
	defer f.Close()
	f.Write([]byte(out))

	return nil
}
