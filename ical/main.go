package main

import (
	"encoding/json"
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
		ID          int       `json:"id"`
		Title       string    `json:"title"`
		Start       time.Time `json:"start"`
		End         time.Time `json:"end"`
		Description string    `json:"description"`
	} `json:"tasks"`
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
			w.WriteHeader(http.StatusInternalServerError)
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
		e.SetCreatedTime(task.Start)
		e.SetStartAt(task.Start)
		e.SetModifiedAt(time.Now())
		e.SetEndAt(task.End)
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
