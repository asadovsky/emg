var smoothie = new SmoothieChart({maxValue: 100, minValue: -100});
smoothie.streamTo(document.getElementById('plot'));
var ts = new TimeSeries();
smoothie.addTimeSeries(ts, {lineWidth: 2, strokeStyle: '#0f0'});

const socket = new WebSocket('ws://' + document.location.host + '/ws');
socket.onclose = function() {
  console.log('close');
};
socket.onmessage = function(ev) {
  const u = JSON.parse(ev.data);
  ts.append(new Date(u.Time), u.Value);
};
