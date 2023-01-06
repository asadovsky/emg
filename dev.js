const plotValuesEl = document.getElementById('plot-values');
const plotLabelsEl = document.getElementById('plot-labels');

const scOpts = {
  responsive: true,
  grid: {strokeStyle: '#333', verticalSections: 0}
};

const scValues = new SmoothieChart(scOpts);
scValues.streamTo(plotValuesEl);
const tsValues = new TimeSeries();
scValues.addTimeSeries(tsValues, {lineWidth: 2, strokeStyle: '#990'});

const scLabels = new SmoothieChart(scOpts);
scLabels.streamTo(plotLabelsEl);
const tsLabels = new TimeSeries();
scLabels.addTimeSeries(tsLabels, {lineWidth: 2, strokeStyle: '#f00'});

const socket = new WebSocket('ws://' + document.location.host + '/ws');
socket.onclose = () => {};
socket.onmessage = ev => {
  const u = JSON.parse(ev.data);
  tsValues.append(new Date(u.Time), u.Value);
};

document.addEventListener('keydown', (ev) => {
  if (ev.key === ' ' && !ev.repeat) {
    const now = Date.now();
    tsLabels.append(new Date(now), 1);
    socket.send(JSON.stringify({Time: now}));
  }
});

function tick() {
  tsLabels.append(new Date(), 0);
  window.requestAnimationFrame(tick);
}
tick();
