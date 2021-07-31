var host = window.location.host;
handlers = {
  restart: (data) => {
    window.location = `http://${host}/lobby.html`;
    console.log(data);
  },
};
function initApp() {
  initLocales();
  try {
    var data = extractJsonFromCookie();
  } catch {
    window.location = `http://${host}/static/index.html`;
  }
  app = Vue.createApp({
    data: function () {
      return data;
    },
    components: {
      "avatar-card": window["avatar-card"],
      "player-list": window["player-list"],
    },
    methods: {
      T(text) {
        return getTranslation(text);
      },
      findPlayer(playerId) {
        return findPlayer(this, playerId);
      },
      getSortedPlayers() {
        let data = this.playersData;
        let result = [];
        Object.keys(data).map(function (key) {
          return result.push([key, data[key]]);
        });
        result = result
          .sort(function (a, b) {
            return a[1].distance - b[1].distance;
          })
          .map((x) => {
            return this.findPlayer(x[0]);
          });
        return result;
      },
      getWinners() {
        let result = this.players
          .filter((player) => {
            return this.playersData[player.id].distance >= 0;
          })
          .sort(function (a, b) {
            if (a.distance < b.distance) return -1;
            if (a.distance > b.distance) return 1;
            return 0;
          });
        return result;
      },
      getLosers() {
        let result = this.players
          .filter((player) => {
            return this.playersData[player.id].distance < 0;
          })
          .sort((a, b) => {
            if (a.distance < b.distance) return -1;
            if (a.distance > b.distance) return 1;
            return 0;
          });
        return result;
      },
      async restartGame() {
        let restart = await post(`http://${host}/c/session/restart`, {
          id: parseInt(this.myId),
          secret: parseInt(this.secret),
          sessionName: this.name,
        });
      },
    },
  });
  endgame = app.mount("#app");
  setupStreamEventHandler({ topic: endgame.name, uid: endgame.myId }, handlers);
}
