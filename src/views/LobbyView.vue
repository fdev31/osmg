<script setup>
import { ref, onMounted } from "vue";
import { RouterLink } from "vue-router";
import { GameSession } from "@/stores/gamesession.js";

const gameSession = GameSession();
console.log("MY NAME IS " + gameSession.getPlayerInfo(gameSession.myId).name);
console.log(gameSession.name);
const name = gameSession.name;
import playerList from "@/components/playerList.vue";

import {
  Toaster,
  any2Obj,
  post,
  setupStreamEventHandler,
  getPlayerInfo,
  getTranslation,
  initLocales,
  setCookie,
  delay,
  kickPlayerVote,
} from "@/lib/utils.js";

const T = getTranslation;

let statuses = {
  NOT_READY: 0,
  READY: 1,
};

const playerlist = ref();

let status = 0;
let hasVoted = false;
const kick_player_threshold = 2;
const toaster = new Toaster();
const host = document.location.host;

async function countDown(count = 4) {
  for (let index = 1; index < count; index++) {
    let display = count - (index + 1) == 0 ? "Go !" : count - (index + 1);
    toaster.show(display, { closeTimeOut: 2000 });
    await delay(1000);
  }
}
const handlers = {
  disconnectPlayer: (data) => {
    toaster.show(
      `${getPlayerInfo(data.id).name} ${getTranslation("is disconnected")}`,
      {
        closeTimeOut: 2500,
      }
    );
  },
  curPlayer: (data) => {
    gameSession.gameData.curPlayer = data.val;
    setCookie(any2Obj(gameSession));
  },
  newPlayer: (data) => {
    delete data["cat"];

    toaster.show(`${data.name} ${getTranslation("enters the game")}`, {
      closeTimeOut: 2500,
    });
    let pd = gameSession.playersData;
    if (pd[data.id] == undefined) {
      pd[data.id] = {};
    }
    gameSession.playersData[data.id] = {};
    gameSession.players.push({ id: data.id, name: data.name });
    for (let newpd of Object.keys(data.playersData)) {
      Object.assign(pd[newpd], data.playersData[newpd]);
    }
    setCookie(any2Obj(gameSession));
  },
  start: async (data) => {
    countDown().then(() => {
      // FIXME
      window.location = `/game_${gameSession.gameType}.html`;
    });
  },
  voteStart: (data) => {
    if (!hasVoted) {
      let player_kicked;
      gameSession.players.map((p) => {
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
            action: (x) => kickPlayerVote(gameSession, player_kicked),
            hideOnClick: true,
          },
          no: {
            action: (x) => kickPlayerVote(gameSession, player_kicked, "false"),
            hideOnClick: true,
          },
        },
      };
      toaster.show(message, options);
    }
    hasVoted = true;
  },
  kickPlayer: (data) => {
    if ((data.result = true)) {
      for (let index = 0; index < gameSession.players.length; index++) {
        if (parseInt(gameSession.players[index].id) == parseInt(data.id)) {
          gameSession.players.splice(index, 1);
        }
      }
      if (gameSession.playersData[data.id] != undefined)
        delete application.playersData[data.id];
    }
    setCookie(any2Obj(gameSession));
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
    hasVoted = false;
    setPlayersById(application);
    setCookie(Vue2Obj(application));
  },
};

initLocales();

setupStreamEventHandler(
  { topic: gameSession.name, uid: gameSession.myId },
  handlers
);

onMounted(() => {
  playerlist.value.players = gameSession.players;
});

function getMainActionText() {
  return [T("Ready"), T("Not ready")][status];
}

async function mainAction() {
  console.log(gameSession.secret);
  switch (status) {
    case statuses.NOT_READY:
      await post(`http://${host}/c/session/start`, {
        id: gameSession.myId,
        sessionName: gameSession.name,
      });
      status = 1;
      break;
    default:
      break;
  }
}
</script>

<template>
  <div id="toaster"></div>
  <div id="app" v-cloak>
    <h2>{{ gameSession.gameType }}</h2>
    <button
      type="button"
      onclick="copyURL('link')"
      :title="T('Click to copy invite link to the clipboard')"
    >
      {{ T("Invite") }}
    </button>
    <input
      size="40"
      type="text"
      id="link"
      :value="`http://${host}/r/${name}`"
    />
    <h3>{{ T("players") }}</h3>
    <playerList
      ref="playerlist"
      :enable-kick="
        !gameSession.gameData.hasVoted &&
        gameSession.players.length > kick_player_threshold
      "
      :kick-text="T('Kick player')"
      :my-id="gameSession.myId"
      v-on:kick="kickPlayerVote"
    >
    </playerList>
    <button v-on:click="mainAction" type="button" class="mainAction">
      {{ getMainActionText() }}
    </button>
    <RouterLink to="/">{{ T("Change game") }}</RouterLink>
  </div>
</template>
