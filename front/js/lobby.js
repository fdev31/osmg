let avatarCode;
let statuses = {
  NOT_READY: 0,
  READY: 1,
};

const kick_player_threshold = 2;
toaster = new Toaster();

function delay(duration = 1000) {
  return new Promise((res) => {
    setTimeout(res, duration);
  });
}
async function countDown(count = 4) {
  for (let index = 1; index < count; index++) {
    let display = count - (index + 1) == 0 ? "Go !" : count - (index + 1);
    toaster.show(display, { closeTimeOut: 2000 });
    await delay(1000);
  }
}
handlers = {
  connectPlayer: (data) => {
    toaster.show(
      `${application._playersById[data.id].name} ${getTranslation(
        "enters the game"
      )}`,
      {
        closeTimeOut: 2500,
      }
    );
    application.playersData[data.id] = {};
    setCookie(Vue2Obj(application));
  },
  disconnectPlayer: (data) => {
    toaster.show(
      `${application._playersById[data.id].name} ${getTranslation(
        "is disconnected"
      )}`,
      {
        closeTimeOut: 2500,
      }
    );
  },
  curPlayer: (data) => {
    application.gameData.curPlayer = data.val;
    setCookie(Vue2Obj(application));
  },
  newPlayer: (data) => {
    delete data["cat"];
    application.players.push(data);
    setPlayersById(application);
    setCookie(Vue2Obj(application));
  },
  start: async (data) => {
    countDown().then(() => {
      window.location = `/game_${application.gameType}.html`;
    });
  },
  voteStart: (data) => {
    if (!application.gameData.hasVoted) {
      let player_kicked;
      application.players.map((p) => {
        if (parseInt(p.id) === parseInt(data.name.split("_")[1]))
          player_kicked = p;
      });
      let message = `${getTranslation("Do you want to kick")} ${
        player_kicked.name
      }`;
      let options = {
        closeTimeOut: -1,
        buttonGroup: {
          yes: {
            action: (x) => kickPlayerVote(application, player_kicked),
            hideOnClick: true,
          },
          no: {
            action: (x) => kickPlayerVote(application, player_kicked, "false"),
            hideOnClick: true,
          },
        },
      };
      toaster.show(message, options);
    }
    application.gameData.hasVoted = true;
  },
  kickPlayer: (data) => {
    let player_kicked = application._playersById[data.id];
    if ((data.result = true)) {
      for (let index = 0; index < application.players.length; index++) {
        if (
          parseInt(application.players[index].id) == parseInt(player_kicked.id)
        ) {
          application.players.splice(index, 1);
        }
      }
      if (application.playersData[player_kicked.id] != undefined)
        delete application.playersData[player_kicked.id];
    }
    setPlayersById(application);
    setCookie(Vue2Obj(application));
  },
  voteEnd: (data) => {
    let message;
    data.result
      ? (message = `End of vote. Player has been kicked!`)
      : (message = `End of vote. Player stay in game`);
    let options = {
      closeTimeOut: 2500,
    };
    toaster.show(getTranslation(message), options);
    application.gameData.hasVoted = false;
    setPlayersById(application);
    setCookie(Vue2Obj(application));
  },
  log: (data) => {
    console.log(data);
  },
};

function initApp() {
  initLocales();
  let data = extractJsonFromCookie();
  data.host = document.location.host;
  data.status = 0;
  data.gameData.hasVoted = false;
  let app = Vue.createApp({
    components: {
      "player-list": window["player-list"],
    },
    watch: {
      players(val) {
        this.$refs.playerlist.players = val;
      },
    },
    data() {
      return data;
    },
    created() {
      setPlayersById(this);
    },
    computed: {
      kickText() {
        return this.T("Kick player");
      },
      enableKick() {
        return (
          !this.gameData.hasVoted && this.players.length > kick_player_threshold
        );
      },
    },
    mounted() {
      document.title = this.T("lobby_title");
      this.$refs.playerlist.players = this.players;
    },
    methods: {
      T(text) {
        return getTranslation(text);
      },
      kickPlayerVote(app, player) {
        kickPlayerVote(app, player);
      },
      playerIsReady: async function () {
        start = await post(`http://${this.host}/c/session/start`, {
          id: this.myId,
          sessionName: this.name,
        });
        this.status = 1;
      },
      playerNotReady: function () {
        // this.status = 0;
      },
      mainAction: function () {
        switch (this.status) {
          case statuses.NOT_READY:
            this.playerIsReady();
            break;
          case statuses.READY:
            this.playerNotReady();
            break;
          default:
            this.playerNotReady();
            break;
        }
      },
      getMainActionText: function () {
        return [this.T("Ready"), this.T("Not ready")][this.status];
      },
    },
  });
  application = app.mount("#app");
  setupStreamEventHandler(
    { topic: application.name, uid: application.myId },
    handlers
  );
}
