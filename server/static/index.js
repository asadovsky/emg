import {Plot} from './plot.js';

const playerOverlayEl = document.getElementById('player-overlay');
const plotEl = document.getElementById('plot');
const timerEl = document.getElementById('timer');

class TimerView {
  constructor(el, initTimeLeft) {
    this.initTimeLeft_ = initTimeLeft;
    this.el_ = document.createElement('div');
    this.el_.style.position = 'absolute';
    this.el_.style.bottom = '0';
    this.el_.style.width = '100%';
    this.onUpdate(initTimeLeft);
    el.appendChild(this.el_);
  }

  onUpdate(timeLeft) {
    const frac = timeLeft / this.initTimeLeft_;
    this.el_.style.height = 100 * frac + '%';
    const colors = ['crimson', 'goldenrod', 'seagreen'];
    const idx = Math.min(colors.length - 1, Math.trunc(colors.length * frac));
    this.el_.style.backgroundColor = colors[idx];
    playerOverlayEl.style.opacity = idx > 0 ? 0 : 0.7;
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

  start() {
    if (this.running_) return;
    this.lastUpdateTime_ = Date.now();
    this.running_ = true;
    this.epoch_++;
    this.tick_(this.epoch_);
  }

  pause() {
    if (!this.running_) return;
    this.update_();
    this.running_ = false;
  }

  reset() {
    this.timeLeft_ = this.initTimeLeft_;
    this.view_.onUpdate(this.timeLeft_);
    this.running_ = false;
  }

  update_() {
    console.assert(this.running_);
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

  tick_(epoch) {
    if (!this.running_ || epoch !== this.epoch_) return;
    this.update_();
    if (this.running_) {
      window.requestAnimationFrame(() => {
        this.tick_(epoch);
      });
    }
  }
}

let player;

const timer = (() => {
  const t = new URLSearchParams(window.location.search).get('t');
  return new Timer(timerEl, t ? parseInt(t) : 10, () => {
    player.pauseVideo();
  });
})();

// https://developers.google.com/youtube/iframe_api_reference
window.onYouTubeIframeAPIReady = () => {
  const v = new URLSearchParams(window.location.search).get('v');
  player = new YT.Player('player-iframe', {
    videoId: v || 'p_LVOPX37SY',
    playerVars: {
      controls: 0,
      disablekb: 1,
      fs: 0,
      modestbranding: 1,
      mute: 0,
      rel: 0,
    },
    events: {
      onReady: (ev) => {
        player.seekTo(0, true);
        ev.target.playVideo();
      },
      onStateChange: (ev) => {
        switch (ev.data) {
          case 1: {
            timer.reset();
            timer.start();
            break;
          }
          case 2: {
            timer.pause();
            break;
          }
        }
        // Restore focus to window so the keydown listener keeps triggering.
        window.focus();
      },
      onError: (ev) => {
        console.error(ev.data);
      },
    },
  });
};

const scriptEl = document.createElement('script');
scriptEl.src = 'https://www.youtube.com/iframe_api';
document.head.appendChild(scriptEl);

const plot = new Plot(plotEl);

const socket = new WebSocket('ws://' + document.location.host + '/ws');
socket.onmessage = (ev) => {
  const u = JSON.parse(ev.data);
  plot.handleUpdate(u);
  if (u.Pred) {
    timer.reset();
    timer.start();
    if (player && player.getPlayerState() === 2) {
      player.playVideo();
    }
  }
};

document.addEventListener('keydown', (ev) => {
  if (ev.key === 'p' && !ev.repeat) {
    plotEl.style.display =
      window.getComputedStyle(plotEl).display === 'none' ? 'block' : 'none';
  }
});
