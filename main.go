package main

import (
	"bufio"
	"container/ring"
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

type Update struct {
	Time  int64
	Reset bool
	Value float32
	Label bool
	Pred  bool
}

type hub struct {
	clients     map[chan<- []byte]bool
	subscribe   chan chan<- []byte
	unsubscribe chan chan<- []byte
	broadcast   chan *Update
	record      chan *Update
	r           *ring.Ring
	n           int
	mean        float32
	variance    float32
}

const windowSize = 100 // 1 second of sensor readings

func newHub() *hub {
	return &hub{
		clients:     make(map[chan<- []byte]bool),
		subscribe:   make(chan chan<- []byte),
		unsubscribe: make(chan chan<- []byte),
		broadcast:   make(chan *Update),
		record:      make(chan *Update),
		r:           ring.New(windowSize),
	}
}

func (h *hub) handleUpdate(u *Update) ([]byte, error) {
	if u.Time == 0 {
		u.Time = time.Now().UnixMilli()
	}
	if *recordFile != "" {
		h.record <- u
	}
	if u.Label {
		return json.Marshal(u)
	}
	value := u.Value
	if h.n == windowSize {
		sigmaRatio := float32(math.Abs(float64(value-h.mean)) / math.Sqrt(float64(h.variance)))
		if sigmaRatio > 2 {
			u.Pred = true
		}
	}
	oldMean := h.mean
	if h.n < windowSize {
		// Welford's algorithm.
		h.n++
		h.mean += (value - h.mean) / float32(h.n)
		h.variance += (value - h.mean) * (value - oldMean)
		if h.n == windowSize {
			h.variance /= windowSize - 1
		}
	} else {
		// https://jonisalonen.com/2014/efficient-and-accurate-rolling-standard-deviation/
		oldValue := h.r.Value.(float32)
		h.mean += (value - oldValue) / windowSize
		h.variance += (value - oldValue) * (value - h.mean + oldValue - oldMean) / (windowSize - 1)
	}
	h.r.Value = value
	h.r = h.r.Next()
	return json.Marshal(u)
}

func (h *hub) listen() {
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
			h.broadcast <- &Update{Time: uTime.UnixMilli(), Value: float32(math.Sin(2 * math.Pi * uTime.Sub(startTime).Seconds()))}
			time.Sleep(10 * time.Millisecond)
		}
	} else {
		for {
			stream, err := serial.OpenPort(&serial.Config{Name: *arduinoPort, Baud: 115200})
			if !os.IsNotExist(err) {
				ok(err)
				scanner := bufio.NewScanner(stream)
				for scanner.Scan() {
					v, err := strconv.ParseFloat(scanner.Text(), 32)
					ok(err)
					h.broadcast <- &Update{Value: float32(v)}
				}
				ok(scanner.Err())
			}
			time.Sleep(time.Second)
		}
	}
}

func (h *hub) run() {
	go h.listen()
	if *recordFile != "" {
		go func() {
			f, err := os.Create(*recordFile)
			ok(err)
			defer f.Close()
			for {
				buf, err := json.Marshal(<-h.record)
				ok(err)
				buf = append(buf, '\n')
				_, err = f.Write(buf)
				ok(err)
			}
		}()
	}
	for {
		select {
		case c := <-h.subscribe:
			h.clients[c] = true
		case c := <-h.unsubscribe:
			delete(h.clients, c)
		case u := <-h.broadcast:
			buf, err := h.handleUpdate(u)
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
		for {
			err := conn.WriteMessage(websocket.TextMessage, <-send)
			if err != websocket.ErrCloseSent && !errors.Is(err, syscall.EPIPE) {
				ok(err)
			}
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

func main() {
	flag.Parse()
	if *replayFile != "" {
		assert(*recordFile == "")
		assert(!*fakeData)
	}
	h := newHub()
	go h.run()
	cwd, err := os.Getwd()
	ok(err)
	http.Handle("/", http.FileServer(http.Dir(cwd)))
	http.HandleFunc("/ws", h.handleWebSocket)
	httpAddr := fmt.Sprintf("localhost:%d", *httpPort)
	ok(http.ListenAndServe(httpAddr, nil))
}
