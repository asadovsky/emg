const SC_OPTS = {
  responsive: true,
  grid: {strokeStyle: '#333', verticalSections: 0},
};

function mkCanvas() {
  const res = document.createElement('canvas');
  res.style.display = 'block';
  res.style.width = '100%';
  res.style.height = '200px';
  return res;
}

export class Plot {
  constructor(el) {
    const valuesEl = mkCanvas();
    el.appendChild(valuesEl);
    const scValues = new SmoothieChart(SC_OPTS);
    scValues.streamTo(valuesEl);
    this.tsValues_ = new TimeSeries();
    scValues.addTimeSeries(this.tsValues_, {
      lineWidth: 2,
      strokeStyle: '#990',
      interpolation: 'linear',
    });

    const labelsAndPredsEl = mkCanvas();
    el.appendChild(labelsAndPredsEl);
    const scLabelsAndPreds = new SmoothieChart(SC_OPTS);
    scLabelsAndPreds.streamTo(labelsAndPredsEl);
    this.tsLabels_ = new TimeSeries();
    scLabelsAndPreds.addTimeSeries(this.tsLabels_, {
      lineWidth: 2,
      strokeStyle: '#f00',
      interpolation: 'step',
    });
    this.tsPreds_ = new TimeSeries();
    scLabelsAndPreds.addTimeSeries(this.tsPreds_, {
      lineWidth: 2,
      strokeStyle: '#09f',
      interpolation: 'step',
    });
  }

  handleUpdate(u) {
    if (u.Reset) {
      this.tsValues_.clear();
      this.tsLabels_.clear();
      this.tsPreds_.clear();
      return;
    }
    this.tsLabels_.append(new Date(u.Time - 1), 0);
    this.tsPreds_.append(new Date(u.Time - 1), 0);
    if (u.Label) {
      this.tsLabels_.append(new Date(u.Time), 1);
      this.tsLabels_.append(new Date(u.Time + 1), 0);
      return;
    }
    if (u.Pred) {
      this.tsPreds_.append(new Date(u.Time), 1);
      this.tsPreds_.append(new Date(u.Time + 1), 0);
    }
    console.assert(u.Value !== undefined);
    this.tsValues_.append(new Date(u.Time), u.Value);
  }
}
