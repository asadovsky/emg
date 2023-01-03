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
    this.onUpdate(initTimeLeft);
    el.appendChild(this.el_);
  }
  onUpdate(timeLeft) {
    const frac = timeLeft / this.initTimeLeft_;
    this.el_.style.height = this.maxHeight_ * frac + 'px';
    this.el_.style.backgroundColor =
      frac > 0.6 ? 'seagreen' : (frac > 0.3 ? 'goldenrod' : 'crimson');
  }
}

class Timer {
  constructor(el, initTimeLeft, onFire) {
    this.view_ = new TimerView(el, initTimeLeft);
    this.initTimeLeft_ = initTimeLeft;
    this.onFire_ = onFire;
    this.timeLeft_ = initTimeLeft;
    this.lastUpdateTime_ = 0;
    this.running_ = false;
    this.epoch_ = 0;
  }
  update_() {
    const now = Date.now();
    this.timeLeft_ -= (now - this.lastUpdateTime_) / 1000;
    this.timeLeft_ = Math.max(0, this.timeLeft_);
    this.lastUpdateTime_ = now;
    this.view_.onUpdate(this.timeLeft_);
    if (this.timeLeft_ === 0) {
      this.running_ = false;
      this.onFire_();
    }
  }
  start() {
    if (this.running_) return;
    this.lastUpdateTime_ = Date.now();
    this.running_ = true;
    this.epoch_++;
    this.tick_(this.epoch_);
  }
  pause() {
    this.update_();
    this.running_ = false;
  }
  reset() {
    this.timeLeft_ = this.initTimeLeft_;
    this.view_.onUpdate(this.timeLeft_);
    this.running_ = false;
  }
  tick_(epoch) {
    if (!this.running_ || epoch !== this.epoch_) return;
    this.update_();
    if (this.running_) {
      window.requestAnimationFrame(() => {this.tick_(epoch);});
    }
  }
}

let player;

const timer = new Timer(timerEl, 5, () => {player.pauseVideo();});

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