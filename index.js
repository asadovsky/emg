const smoothie = new SmoothieChart();
smoothie.streamTo(document.getElementById('plot'));
const ts = new TimeSeries();
smoothie.addTimeSeries(ts, {lineWidth: 2, strokeStyle: '#0f0'});

const socket = new WebSocket('ws://' + document.location.host + '/ws');
socket.onclose = () => {};
socket.onmessage = (ev) => {
  const u = JSON.parse(ev.data);
  ts.append(new Date(u.Time), u.Value);
};

let player;
function onYouTubeIframeAPIReady() {  // jshint ignore:line
  player = new YT.Player('player', {  // jshint ignore:line
    height: '450',
    width: '800',
    videoId: 'p_LVOPX37SY',
    playerVars: {
      'controls': 0,
      'disablekb': 1,
      'modestbranding': 1,
      'mute': 1,
      'rel': 0
    },
    events: {
      'onReady': (ev) => {},
      'onStateChange': (ev) => {},
      'onError': (ev) => {}
    }
  });
}

const scriptEl = document.createElement('script');
scriptEl.src = 'https://www.youtube.com/iframe_api';
document.head.appendChild(scriptEl);
