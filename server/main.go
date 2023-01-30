package main

import (
	"bufio"
	"embed"
	"encoding/json"
	"errors"
	"flag"
	"fmt"
	"github.com/gorilla/websocket"
	"math"
	"net/http"
	"os"
	"strconv"
	"syscall"
	"time"

	"github.com/tarm/serial"
)

var httpPort = flag.Int("http-port", 4000, "")
var arduinoPort = flag.String("arduino-port", "", "")
var fakeData = flag.Bool("fake-data", false, "generate sinusoidal data")
var recordFile = flag.String("record-file", "", "record data to this file")
var replayFile = flag.String("replay-file", "", "replay data from this file")

func ok(err error, v ...interface{}) {
	if err != nil {
		panic(fmt.Sprintf("%v: %s", err, fmt.Sprint(v...)))
	}
}

func assert(b bool, v ...interface{}) {
	if !b {
		panic(fmt.Sprint(v...))
	}
}

func readUpdatesFromFile(name string) ([]Update, error) {
	f, err := os.Open(name)
	if err != nil {
		return nil, err
	}
	defer f.Close()
	var res []Update
	scanner := bufio.NewScanner(f)
	for scanner.Scan() {
		var u Update
		err := json.Unmarshal(scanner.Bytes(), &u)
		if err != nil {
			return nil, err
		}
		res = append(res, u)
	}
	if err := scanner.Err(); err != nil {
		return nil, err
	}
	return res, nil
}

func streamUpdatesToFile(name string, c <-chan *Update) {
	f, err := os.Create(*recordFile)
	ok(err)
	defer f.Close()
	for u := range c {
		buf, err := json.Marshal(u)
		ok(err)
		buf = append(buf, '\n')
		_, err = f.Write(buf)
		ok(err)
	}
}

type Update struct {
	Time  int64
	Reset bool     `json:",omitempty"`
	Value *float32 `json:",omitempty"`
	Label bool     `json:",omitempty"`
	Pred  bool     `json:",omitempty"`
}

type hub struct {
	clients     map[chan<- []byte]bool
	subscribe   chan chan<- []byte
	unsubscribe chan chan<- []byte
	broadcast   chan *Update
	record      chan *Update
	stats       *StreamStats
}

func newHub() *hub {
	return &hub{
		clients:     make(map[chan<- []byte]bool),
		subscribe:   make(chan chan<- []byte),
		unsubscribe: make(chan chan<- []byte),
		broadcast:   make(chan *Update),
		record:      make(chan *Update),
		stats:       NewStreamStats(),
	}
}

func (h *hub) generateUpdates() {
	if *replayFile != "" {
		updates, err := readUpdatesFromFile(*replayFile)
		ok(err)
		assert(len(updates) > 0)
		for {
			startTime := time.Now()
			firstTime := time.UnixMilli(updates[0].Time)
			for _, u := range updates {
				uTime := startTime.Add(time.UnixMilli(u.Time).Sub(firstTime))
				// Sleep until 5ms before this update should be plotted.
				time.Sleep(uTime.Sub(time.Now()) - 5*time.Millisecond)
				h.broadcast <- &Update{Time: uTime.UnixMilli(), Value: u.Value, Label: u.Label}
			}
			// Sleep for 1s, then reset.
			time.Sleep(time.Second)
			h.broadcast <- &Update{Reset: true}
		}
	} else if *fakeData {
		startTime := time.Now()
		for {
			uTime := time.Now()
			v := float32(math.Sin(2 * math.Pi * uTime.Sub(startTime).Seconds()))
			h.broadcast <- &Update{Time: uTime.UnixMilli(), Value: &v}
			time.Sleep(10 * time.Millisecond)
		}
	} else {
		for {
			stream, err := serial.OpenPort(&serial.Config{Name: *arduinoPort, Baud: 115200})
			if !os.IsNotExist(err) {
				ok(err)
				scanner := bufio.NewScanner(stream)
				for scanner.Scan() {
					f, err := strconv.ParseFloat(scanner.Text(), 32)
					ok(err)
					v := float32(f)
					h.broadcast <- &Update{Value: &v}
				}
				ok(scanner.Err())
			}
			time.Sleep(time.Second)
		}
	}
}

func (h *hub) run() {
	go h.generateUpdates()
	if *recordFile != "" {
		go streamUpdatesToFile(*recordFile, h.record)
	}
	for {
		select {
		case c := <-h.subscribe:
			h.clients[c] = true
		case c := <-h.unsubscribe:
			delete(h.clients, c)
		case u := <-h.broadcast:
			if u.Time == 0 {
				u.Time = time.Now().UnixMilli()
			}
			if *recordFile != "" {
				h.record <- u
			}
			if u.Value != nil {
				h.stats.Push(*u.Value)
				if h.stats.Full() {
					u.Pred = h.stats.Pred()
				}
			}
			buf, err := json.Marshal(u)
			ok(err)
			for send := range h.clients {
				send <- buf
			}
		}
	}
}

func (h *hub) handleWebSocket(w http.ResponseWriter, r *http.Request) {
	conn, err := websocket.Upgrade(w, r, nil, 0, 0)
	ok(err)
	send := make(chan []byte)
	h.subscribe <- send

	go func() {
		for buf := range send {
			err := conn.WriteMessage(websocket.TextMessage, buf)
			if err == websocket.ErrCloseSent || errors.Is(err, syscall.EPIPE) {
				break
			}
			ok(err)
		}
	}()

	for {
		_, _, err := conn.ReadMessage()
		if websocket.IsCloseError(err, websocket.CloseGoingAway) {
			break
		}
		ok(err)
		h.broadcast <- &Update{Label: true}
	}

	h.unsubscribe <- send
	close(send)
	conn.Close()
}

//go:embed *.css *.html *.js
var content embed.FS

func main() {
	flag.Parse()
	if *replayFile != "" {
		assert(*recordFile == "")
		assert(!*fakeData)
	}
	h := newHub()
	go h.run()
	http.Handle("/", http.FileServer(http.FS(content)))
	http.HandleFunc("/ws", h.handleWebSocket)
	httpAddr := fmt.Sprintf("localhost:%d", *httpPort)
	ok(http.ListenAndServe(httpAddr, nil))
}
