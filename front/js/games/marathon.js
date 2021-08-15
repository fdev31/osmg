const statuses = {
  UNINITIALIZED: 0,
  THROW: 1,
  DICE_THROWN: 2,
  WAITING: 3,
  END_TURN: 4,
  GAME_OVER: 5,
  GAME_WON: 6,
  ERROR: 7,
};
function isError(res) {
  return res && res.detail != undefined;
}

function checkLost() {
  if (application.distance < 0) {
    application.setStatus(statuses.GAME_OVER);
    return true;
  }
}
toaster = new Toaster("toaster");
let host = document.location.host;
handlers = {
  curPlayer: (data) => {
    if (!checkLost()) {
      application.gameData.curPlayer = data.val.toString();
      if (data.val.toString() === application.myId.toString()) {
        application.setStatus(statuses.THROW);
        setTimeout(() => {
          application.$refs.mydice.updateDice([0, 0, 0, 0], false);
          application.$refs.mydice.diceNumber = Math.min(
            4,
            ("" + (application.playersData[application.myId].distance - 1))
              .length
          );
        }, 1);
        toaster.show(getTranslation("It's your turn to play!"), {
          closeTimeOut: 3500,
        });
      }
    }
  },
  connectPlayer: (data) => {
    application.playersData[data.id].disconnected = false;
    toaster.show(
      `${findPlayer(application, data.id).name} ${getTranslation(
        "enters the game"
      )}`,
      {
        closeTimeOut: 2500,
      }
    );
  },
  disconnectPlayer: (data) => {
    application.playersData[data.id].disconnected = true;
    toaster.show(
      `${findPlayer(application, data.id).name} ${getTranslation(
        "is disconnected"
      )}`,
      {
        closeTimeOut: 2500,
      }
    );
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
            action: () => window.kickPlayerVote(application, player_kicked),
            hideOnClick: true,
          },
          no: {
            action: () =>
              window.kickPlayerVote(application, player_kicked, "false"),
            hideOnClick: true,
          },
        },
      };
      toaster.show(message, options);
    }
    application.gameData.hasVoted = true;
  },
  kickPlayer: (data) => {
    let player_kicked = findPlayer(application, data.id);
    if (data.id) {
      for (let i = 0; i < application.players.length; i++) {
        if (parseInt(application.players[i].id) == parseInt(player_kicked.id))
          application.players.splice(i, 1);
      }
      if (application.playersData[player_kicked.id] != undefined)
        delete application.playersData[player_kicked.id];
    }
    setCookie(Vue2Obj(application));
    if (parseInt(application.myId) == parseInt(data.id))
      window.location = `http://${host}/index.html`;
  },
  voteEnd: (data) => {
    let message;
    data.result
      ? (message = "Fin du vote. Le joueur a été renvoyé du jeu!")
      : (message = "Fin du vote. Le joueur reste en jeu");
    toaster.show(getTranslation(message), { closeTimeOut: 2500 });
    application.gameData.hasVoted = false;
    setCookie(Vue2Obj(application));
  },
  varUpdate: (data) => {
    if (data.player) {
      let pd = application.playersData[data.player];
      if (pd === undefined) {
        pd = application.playersData[data.player] = {};
      }
      if (data.player != application.myId) {
        toaster.show(
          `${findPlayer(application, data.player).name} avance de ${
            parseInt(application.playersData[data.player].distance) -
            parseInt(data.val)
          } mètres`
        );
      }
      application.animateProgressBar(data.player, pd.distance, data.val);
    } else {
      application.gameData[data.var] = data.val;
    }
    checkLost();
  },
  newTurn: (data) => {
    checkLost();
    application.gameData.turn = data.val;
  },
  endOfGame: (data) => {
    message = data.message;
    let myStatus = statuses.GAME_OVER;
    for (let player of application.players) {
      if (player.id == data.player) {
        message += "\nPlayer " + player.name + " wins!";
        if (player.id == application.myId) myStatus = statuses.GAME_WON;
      }
    }
    application.setStatus(myStatus);
    application.gameData.turn = 0;
    setCookie(Vue2Obj(application));
    window.location = "endgame.html";
  },
};

let _initialized = false;
function initApp() {
  if (_initialized) return;
  _initialized = true;

  initLocales();

  try {
    var data = extractJsonFromCookie();
  } catch (e) {
    window.location = `http://${host}/index.html`;
  }

  data.gameData.hasVoted = false;
  if (typeof data.name == "undefined" || data.name == null) {
    window.location = `http://${host}/lobby.html`;
  }
  if (data.status == undefined) {
    // please do not remove this check, it was a huge bug...
    // if you do so for some reason, we need to discuss solutions
    // Do not remove code which has been added if you don't know what it's doing ;)
    Object.assign(data, {
      host: document.location.host,
      status: 0,
    });
  }
  app = Vue.createApp({
    data: function () {
      return data;
    },
    components: {
      "player-list": window["player-list"],
      "dice-single": window["dice"],
      "dice-array": window["dicearray"],
      "avatar-card": window["avatar-card"],
    },
    watch: {
      players(newVal) {
        this.$refs.playerlist.players = newVal;
      },
    },
    mounted() {
      document.title = this.T("marathon_title");
      this.$refs.playerlist.players = this.players;
      this.animateRuleButton(12);
    },
    computed: {
      isLastAction() {
        return statuses.DICE_THROWN == this.status;
      },
      diceVisible() {
        return [statuses.THROW, statuses.DICE_THROWN].includes(this.status);
      },
      distance() {
        return this.playersData[this.myId]
          ? this.playersData[this.myId].distance
          : 0;
      },
      kickText() {
        return this.T("Kick player");
      },
      sortPlayers() {
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
            return Object.assign(findPlayer(this, x[0]), x[1]);
          });
        return result;
      },
    },
    methods: {
      T(text) {
        return getTranslation(text);
      },
      didIWin() {
        return this.status == statuses.GAME_WON;
      },
      didILose() {
        return this.status == statuses.GAME_OVER;
      },
      playerName() {
        for (let p of this.players) {
          if (p.id == this.myId) return p.name;
        }
      },
      setStatus(status) {
        this.status = status;
        setCookie(Vue2Obj(this));
      },
      getPlayerAction: function () {
        return [
          this.T("Waiting for other players"),
          this.T("Throw dices"),
          this.T("Move forward"),
          this.T("Wait"),
          this.T("End of Turn"),
          this.T("Game won"),
          this.T("Game"),
          this.T("Error"),
        ][this.status];
      },
      showPlayerStatus: function (player) {
        if (parseInt(this.gameData.curPlayer) === parseInt(player.id)) {
          return "playing";
        }
      },
      async mainPlayButton() {
        switch (this.status) {
          case statuses.THROW:
            await this.throw_dices();
            break;
          case statuses.DICE_THROWN:
            await this.player_advance();
            break;
        }
      },
      async throw_dices() {
        try {
          let diceArray = await post(`http://${host}/g/marathon/throwDice`, {
            id: parseInt(this.myId),
            secret: parseInt(this.secret),
            sessionName: this.name,
          });
          this.setStatus(statuses.DICE_THROWN);

          let dice = this.$refs["mydice"];
          dice.diceNumber = diceArray.length;
          dice.updateDice(diceArray);
          dice.enableDrag(true);
        } catch (e) {
          toaster.show(e.message, { closeTimeOut: 10000 });
          this.setStatus(statuses.ERROR);
        }
      },
      async skipTurn() {
        await this.player_advance(0);
      },
      getProgress(id) {
        return (
          100 * ((42195 - this.playersData[`${id}`].distance) / 42195) || 0
        );
      },
      findPlayer(id) {
        for (var [key, player] of Object.entries(this.playersData)) {
          if (key == id) {
            return player;
          }
        }
      },
      animateProgressBar(id, start, stop, fps = 120) {
        let distInterval = Math.floor((start - stop) / 20);
        let intervalId = setInterval(() => {
          this.playersData[`${id}`].distance -= distInterval;
          if (this.playersData[`${id}`].distance < stop) {
            clearInterval(intervalId);
            this.playersData[`${id}`].distance = stop;
          }
        }, Math.floor(3600 / fps));
      },
      showRules() {
        let closeBtn = {
          close: {
            hideOnClick: true,
          },
        };
        toaster.show(this.T("marathon_rules"), {
          closeTimeOut: -1,
          buttonGroup: closeBtn,
        });
      },
      animateRuleButton(fps, duration = 5000) {
        let btn = document.getElementById("rules-btn");
        let f = 0;
        let intervalId = setInterval(() => {
          btn.style.color = `rgb(${Math.cos(f) * 255} 100 100)`;
          f++;
        }, 1000 / fps);
        setInterval(() => {
          clearInterval(intervalId);
          btn.style.color = `unset`;
        }, duration);
      },
      async player_advance(value) {
        let choice =
          value === undefined
            ? this.$refs.mydice.getDiceValues().join("")
            : value;

        let action = await post(
          `http://${host}/g/marathon/validateDice?value=${choice}`,
          {
            id: parseInt(this.myId),
            secret: parseInt(this.secret),
            sessionName: this.name,
          }
        );
        if (isError(action)) {
          alert(action.detail);
        } else {
          this.setStatus(statuses.END_TURN);
        }
      },
      kickPlayerVote() {
        window.kickPlayerVote();
      },
    },
  });
  application = app.mount("#app");
  parseInt(application.gameData.curPlayer) === parseInt(application.myId)
    ? application.setStatus(statuses.THROW)
    : application.setStatus(statuses.WAITING);
  setupStreamEventHandler(
    { topic: application.name, uid: application.myId },
    handlers
  );
  if (parseInt(application.gameData.turns) == 0) {
    for (const key in application.playersData) {
      if (Object.hasOwnProperty.call(application.playersData, key)) {
        application.playersData[key].distance = 42195;
      }
    }
  }
}
