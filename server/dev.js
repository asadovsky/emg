import {Plot} from './plot.js';

const plotEl = document.getElementById('plot');

const plot = new Plot(plotEl);

const socket = new WebSocket('ws://' + document.location.host + '/ws');
socket.onmessage = (ev) => {
  const u = JSON.parse(ev.data);
  plot.handleUpdate(u);
};

document.addEventListener('keydown', (ev) => {
  if (ev.key === ' ' && !ev.repeat) {
    socket.send('');
  }
});
