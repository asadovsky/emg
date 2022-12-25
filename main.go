package main

import (
	"bufio"
	"encoding/json"
	"flag"
	"fmt"
	"github.com/gorilla/websocket"
	"log"
	"net/http"
	"os"
	"time"

	"github.com/tarm/serial"
)

var httpPort = flag.Int("http-port", 4000, "")
var arduinoPort = flag.String("arduino-port", "", "")

func ok(err error, v ...interface{}) {
	if err != nil {
		panic(fmt.Sprintf("%v: %s", err, fmt.Sprint(v...)))
	}
}

type Update struct {
	Text string
	Time int64
}

type hub struct {
	clients     map[chan<- []byte]bool
	subscribe   chan chan<- []byte
	unsubscribe chan chan<- []byte
	broadcast   chan []byte
}

func newHub() *hub {
	return &hub{
		clients:     make(map[chan<- []byte]bool),
		subscribe:   make(chan chan<- []byte),
		unsubscribe: make(chan chan<- []byte),
		broadcast:   make(chan []byte),
	}
}

func (h *hub) listen() {
	for {
		stream, err := serial.OpenPort(&serial.Config{Name: *arduinoPort, Baud: 115200})
		if !os.IsNotExist(err) {
			ok(err)
			scanner := bufio.NewScanner(stream)
			for scanner.Scan() {
				u := &Update{
					Text: scanner.Text(),
					Time: time.Now().UnixMilli(),
				}
				buf, err := json.Marshal(u)
				ok(err)
				h.broadcast <- buf
			}
			ok(scanner.Err())
		}
		time.Sleep(time.Second)
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
			if err != websocket.ErrCloseSent {
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
