const plotValuesEl = document.getElementById('plot-values');
const plotLabelsEl = document.getElementById('plot-labels');

const scOpts = {
  responsive: true,
  grid: {strokeStyle: '#333', verticalSections: 0},
};

const scValues = new SmoothieChart(scOpts);
scValues.streamTo(plotValuesEl);
const tsValues = new TimeSeries();
scValues.addTimeSeries(tsValues, {
  lineWidth: 2,
  strokeStyle: '#990',
  interpolation: 'linear',
});

const scLabels = new SmoothieChart(scOpts);
scLabels.streamTo(plotLabelsEl);
const tsLabels = new TimeSeries();
scLabels.addTimeSeries(tsLabels, {
  lineWidth: 2,
  strokeStyle: '#f00',
  interpolation: 'step',
});
const tsPreds = new TimeSeries();
scLabels.addTimeSeries(tsPreds, {
  lineWidth: 2,
  strokeStyle: '#66f',
  interpolation: 'step',
});

const socket = new WebSocket('ws://' + document.location.host + '/ws');
socket.onclose = () => {};
socket.onmessage = (ev) => {
  const u = JSON.parse(ev.data);
  if (u.Reset) {
    tsValues.clear();
    tsLabels.clear();
    tsPreds.clear();
    return;
  }
  const d = new Date(u.Time);
  tsLabels.append(new Date(u.Time - 1), 0);
  tsPreds.append(new Date(u.Time - 1), 0);
  if (u.Label) {
    tsLabels.append(d, 1);
    return;
  }
  if (u.Pred) {
    tsPreds.append(d, 1);
  }
  console.assert(u.Value !== undefined);
  tsValues.append(d, u.Value);
};

document.addEventListener('keydown', (ev) => {
  if (ev.key === ' ' && !ev.repeat) {
    socket.send('');
  }
});