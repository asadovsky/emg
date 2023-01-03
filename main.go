package main

import (
	"bufio"
	"container/ring"
	"encoding/json"
	"errors"
	"flag"
	"fmt"
	"github.com/gorilla/websocket"
	"log"
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
var fakeData = flag.Bool("fake-data", false, "")

func ok(err error, v ...interface{}) {
	if err != nil {
		panic(fmt.Sprintf("%v: %s", err, fmt.Sprint(v...)))
	}
}

type Update struct {
	Time       int64
	Value      float32
	SigmaRatio float32
}

type hub struct {
	clients     map[chan<- []byte]bool
	subscribe   chan chan<- []byte
	unsubscribe chan chan<- []byte
	broadcast   chan []byte
	r           *ring.Ring
	n           int
	mean        float32
	variance    float32
}

const windowSize = 1000

func newHub() *hub {
	return &hub{
		clients:     make(map[chan<- []byte]bool),
		subscribe:   make(chan chan<- []byte),
		unsubscribe: make(chan chan<- []byte),
		broadcast:   make(chan []byte),
		r:           ring.New(windowSize),
	}
}

func (h *hub) handleUpdate(value float32) error {
	var sigmaRatio float32 = -1
	if h.n == windowSize && h.variance > 0 {
		sigmaRatio = float32(math.Abs(float64(value-h.mean)) / math.Sqrt(float64(h.variance)))
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
	buf, err := json.Marshal(&Update{
		Time:       time.Now().UnixMilli(),
		Value:      value,
		SigmaRatio: sigmaRatio,
	})
	if err != nil {
		return err
	}
	h.broadcast <- buf
	return nil
}

func (h *hub) listen() {
	if *fakeData {
		startTime := time.Now().UnixMilli()
		for {
			t := float64(time.Now().UnixMilli()-startTime) / 1000
			ok(h.handleUpdate(float32(100 * math.Sin(2*math.Pi*t))))
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
					ok(h.handleUpdate(float32(v)))
				}
				ok(scanner.Err())
			}
			time.Sleep(time.Second)
		}
	}
}

func (h *hub) run() {
	go h.listen()
	for {
		select {
		case c := <-h.subscribe:
			h.clients[c] = true
		case c := <-h.unsubscribe:
			delete(h.clients, c)
		case msg := <-h.broadcast:
			for send := range h.clients {
				send <- msg
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

	_, buf, err := conn.ReadMessage()
	if !websocket.IsCloseError(err, websocket.CloseGoingAway) {
		ok(err)
		log.Fatalf("unexpected message from client: %v", buf)
	}

	h.unsubscribe <- send
	close(send)
	conn.Close()
}

func main() {
	flag.Parse()
	h := newHub()
	go h.run()
	cwd, err := os.Getwd()
	ok(err)
	http.Handle("/", http.FileServer(http.Dir(cwd)))
	http.HandleFunc("/ws", h.handleWebSocket)
	httpAddr := fmt.Sprintf("localhost:%d", *httpPort)
	ok(http.ListenAndServe(httpAddr, nil))
}
