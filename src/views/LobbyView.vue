<script setup>
import { ref, onMounted, watchEffect } from "vue";
import { RouterLink } from "vue-router";
import { GameSession } from "@/stores/gamesession.js";
import playerList from "@/components/playerList.vue";

const gameSession = GameSession();
const name = gameSession.name;

import {
  post,
  setupStreamEventHandler,
  getTranslation as T,
  initLocales,
  copyURL,
  setCookie,
  delay,
} from "@/lib/utils.js";

import { kickPlayerVote } from "@/lib/voting.js";
import { Toaster } from "@/lib/toaster.js";

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
    // FIXME: toaster.show(display, { closeTimeOut: 2000 });
    await delay(1000);
  }
}
const handlers = {
  disconnectPlayer: (data) => {
    toaster.show(
      `${gameSession.getPlayerInfo(data.id).name} ${T("is disconnected")}`,
      {
        closeTimeOut: 2500,
      }
    );
  },
  curPlayer: (data) => {
    gameSession.gameData.curPlayer = data.val;
    setCookie(gameSession.asObject());
  },
  newPlayer: (data) => {
    delete data["cat"];

    /* FIXME

    toaster.show(`${data.name} ${T("enters the game")}`, {
      closeTimeOut: 2500,
    });
    */

    Object.assign(gameSession.playersData, data.playersData);
    Object.assign(gameSession.gameData, data.gameData);
    gameSession.players.push({ id: data.id, name: data.name });

    playerlist.value.players = gameSession.players;
    setCookie(gameSession.asObject());
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
      let message = `${T("Do you want to kick")} ${player_kicked.name}`;
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
    setCookie(gameSession.asObject());
  },
  voteEnd: (data) => {
    let message;
    data.result
      ? (message = `End of vote. Player has been kicked!`)
      : (message = `End of vote. Player stay in game`);
    let options = {
      closeTimeOut: 2500,
    };
    toaster.show(T(message), options);
    hasVoted = false;
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
      @click="copyURL('link')"
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
