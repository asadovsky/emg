const socket = new WebSocket('ws://' + document.location.host + '/ws');
socket.onclose = function() {
  console.log('close');
};
socket.onmessage = function(ev) {
  console.log(ev.data);
};
