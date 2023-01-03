const playerEl = document.getElementById('player');
const timerEl = document.getElementById('timer');
const plotEl = document.getElementById('plot');

const w = 800;
playerEl.style.width = w + 'px';
playerEl.style.height = w * (9 / 16) + 'px';
timerEl.style.height = playerEl.style.height;
plotEl.width = window.innerWidth;
plotEl.height = plotEl.parentElement.offsetHeight;

class TimerView {
  constructor(el, initTimeLeft) {
    this.initTimeLeft_ = initTimeLeft;
    this.maxHeight_ = el.offsetHeight;
    this.el_ = document.createElement('div');
    this.el_.style.position = 'absolute';
    this.el_.style.bottom = '0';
    this.el_.style.width = el.offsetWidth + 'px';
    this.onTick(initTimeLeft);
    el.appendChild(this.el_);
  }
  onTick(timeLeft) {
    const frac = timeLeft / this.initTimeLeft_;
    this.el_.style.height = this.maxHeight_ * frac + 'px';
    this.el_.style.backgroundColor =
      frac > 0.6 ? 'seagreen' : (frac > 0.3 ? 'goldenrod' : 'crimson');
  }
}

class Timer {
  constructor(el, initTimeLeft, onTick) {
    this.view_ = new TimerView(el, initTimeLeft);
    this.initTimeLeft_ = initTimeLeft;
    this.onTick_ = timeLeft => {
      this.view_.onTick(timeLeft);
      onTick(timeLeft);
    };
    this.timeLeft_ = initTimeLeft;
    this.lastTickTime_ = 0;
    this.running_ = false;
    this.epoch_ = 0;
  }
  start() {
    if (this.running_) return;
    this.lastTickTime_ = Date.now();
    this.running_ = true;
    this.epoch_++;
    this.tick_(this.epoch_);
  }
  pause() {
    this.running_ = false;
  }
  reset() {
    this.running_ = false;
    this.timeLeft_ = this.initTimeLeft_;
  }
  tick_(epoch) {
    if (!this.running_ || epoch !== this.epoch_) return;
    const now = Date.now();
    this.timeLeft_ -= (now - this.lastTickTime_) / 1000;
    this.timeLeft_ = Math.max(0, this.timeLeft_);
    this.lastTickTime_ = now;
    this.onTick_(this.timeLeft_);
    if (this.timeLeft_ > 0) {
      window.requestAnimationFrame(() => {this.tick_(epoch);});
    } else {
      this.running_ = false;
    }
  }
}

let player;

const timer = new Timer(timerEl, 10, timeLeft => {
  if (timeLeft === 0) {
    player.pauseVideo();
  }
});

// https://developers.google.com/youtube/iframe_api_reference
function onYouTubeIframeAPIReady() {  // jshint ignore:line
  player = new YT.Player('player', {  // jshint ignore:line
    videoId: 'p_LVOPX37SY',
    playerVars: {
      controls: 0,
      disablekb: 1,
      fs: 0,
      modestbranding: 1,
      mute: 1,
      rel: 0
    },
    events: {
      onReady: ev => {ev.target.playVideo();},
      onStateChange: ev => {
        switch (ev.data) {
          case 1: {
            timer.reset();
            timer.start();
            break;
          }
          case 0:
          case 2: {
            timer.pause();
            break;
          }
        }
      },
      onError: ev => {console.error(ev.data);}
    }
  });
}

const scriptEl = document.createElement('script');
scriptEl.src = 'https://www.youtube.com/iframe_api';
document.head.appendChild(scriptEl);

const smoothie = new SmoothieChart({grid: {strokeStyle: '#333'}});
smoothie.streamTo(plotEl);
const ts = new TimeSeries();
smoothie.addTimeSeries(ts, {lineWidth: 2, strokeStyle: '#660'});

const socket = new WebSocket('ws://' + document.location.host + '/ws');
socket.onclose = () => {};
socket.onmessage = ev => {
  const u = JSON.parse(ev.data);
  ts.append(new Date(u.Time), u.Value);
};
