let _initialized = false;

const handlers = {};

function initApp() {
  if (_initialized) return;
  _initialized = true;

  initLocales();

  let data = {};
  try {
    data = extractJsonFromCookie();
  } catch (e) {
    window.location = `http://${host}/index.html`;
  }
  if (typeof data.name == "undefined" || data.name == null) {
    window.location = `http://${host}/lobby.html`;
  }

  app = Vue.createApp({
    data: function () {
      return data;
    },
    components: {
      "player-list": window["player-list"],
      "avatar-card": window["avatar-card"],
      "atakks-grid": window["atakks-grid"],
    },
    mounted() {
      this.$refs.playerlist.players = this.players;
    },
    methods: {
      T(text) {
        return getTranslation(text);
      },
      playerName() {
        for (let p of this.players) {
          if (p.id == this.myId) return p.name;
        }
      },
    },
  });

  application = app.mount("#app");
  setupStreamEventHandler(
    { topic: application.name, uid: application.myId },
    handlers
  );
}
