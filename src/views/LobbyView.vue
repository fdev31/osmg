<script setup>
import { ref, computed } from "vue";
import { useRouter } from "vue-router";
import { GameSession } from "@/stores/gamesession.js";
import playerList from "@/components/playerList.vue";
import avatarCard from "@/components/avatarCard.vue";
import ToastNotifs from "@/components/ToastNotifs.vue";
import QrCode from "@/components/QrCode.vue";
import { backToHome } from "@/lib/session.js";

import { kickPlayerVote } from "@/lib/voting.js";
import {
  post,
  setupStreamEventHandler,
  getTranslation as T,
  host,
  initLocales,
  copyURL,
  delay,
} from "@/lib/utils.js";

const router = useRouter();
const gameSession = GameSession();
const joinURL = `${host}/r/${gameSession.name}`;

document.debug = import.meta.env.DEV ? { gameSession } : {};

let statuses = {
  NOT_READY: 0,
  READY: 1,
};

const states = gameSession.uiStates;

if (gameSession.uiStates.status === undefined) {
  states.status = statuses.NOT_READY;
  states.hasVoted = false;
}
const playerlist = ref();
const toaster = ref();

const kick_player_threshold = 2;

async function countDown(count = 4) {
  for (let index = 1; index < count; index++) {
    let display = count - (index + 1) == 0 ? "Go !" : count - (index + 1);
    toaster.value.show(display, { duration: 1000 });
    await delay(1000);
  }
}

const justConnected = new Set();

const handlers = {
  curPlayer: (data) => {
    gameSession.gameData.curPlayer = data.val;
    gameSession.save();
  },
  ready: (data) => {
    gameSession.getPlayerInfo(data.id).ready = true;
    gameSession.save();
  },
  connectPlayer: (data) => {
    gameSession.getPlayerInfo(data.id).disconnected = false;
    gameSession.save();
    if (!justConnected.has(data.id))
      toaster.value.show(
        `Welcome back ${gameSession.getPlayerInfo(data.id).name}!`,
        {
          duration: 2500,
        }
      );
  },
  disconnectPlayer: (data) => {
    gameSession.getPlayerInfo(data.id).disconnected = true;
    gameSession.save();
    toaster.value.show(
      `${gameSession.getPlayerInfo(data.id).name} ${T("is disconnected")}`,
      {
        duration: 2500,
      }
    );
  },
  newPlayer: (data) => {
    const playerId = data.id;
    justConnected.add(playerId);
    setTimeout(() => justConnected.delete(playerId), 500);
    delete data["cat"];

    toaster.value.show(`${data.name} ${T("enters the game")}`, {
      duration: 2500,
    });

    Object.assign(gameSession.playersData, data.playersData);
    Object.assign(gameSession.gameData, data.gameData);
    gameSession.players.push({ id: data.id, name: data.name });
    gameSession.save();
  },
  start: async () => {
    gameSession.started = true;
    gameSession.uiStates = {};
    for (const player of gameSession.players) {
      player.ready = false; // reset lobby state
    }
    gameSession.save();
    countDown().then(() => {
      websocket.close();
      router.push(`/game-${gameSession.gameType}`);
    });
  },
  voteStart: (data) => {
    if (!states.hasVoted) {
      let player_kicked;
      gameSession.players.map((p) => {
        if (parseInt(p.id) === parseInt(data.name.split("_")[1]))
          player_kicked = p;
      });
      let message = `${T("Do you want to kick")} ${player_kicked.name}`;
      let options = {
        duration: -1,
        buttonGroup: {
          yes: {
            action: () => kickPlayerVote(gameSession, player_kicked),
            hideOnClick: true,
          },
          no: {
            action: () => kickPlayerVote(gameSession, player_kicked, "false"),
            hideOnClick: true,
          },
        },
      };
      toaster.value.show(message, options);
    }
    states.hasVoted = true;
  },
  kickPlayer: (data) => {
    if (data.result) {
      for (let index = 0; index < gameSession.players.length; index++) {
        if (parseInt(gameSession.players[index].id) == parseInt(data.id)) {
          gameSession.players.splice(index, 1);
        }
      }
      if (gameSession.playersData[data.id] != undefined)
        delete gameSession.playersData[data.id];
    }
    gameSession.save();
  },
  voteEnd: (data) => {
    let message;
    data.result
      ? (message = `End of vote. Player has been kicked!`)
      : (message = `End of vote. Player stay in game`);
    let options = {
      duration: 2500,
    };
    toaster.value.show(T(message), options);
    states.hasVoted = false;
  },
};

initLocales();

const websocket = setupStreamEventHandler(
  { topic: gameSession.name, uid: gameSession.myId },
  handlers
);

const mainActionText = computed(
  () => [T("Ready"), T("Not ready")][states.status]
);

async function mainAction() {
  switch (states.status) {
    case statuses.NOT_READY:
      states.status = statuses.READY;
      gameSession.save();
      await post(`/c/session/start`, {
        id: gameSession.myId,
        sessionName: gameSession.name,
      });
      break;
    default:
      break;
  }
}
</script>

<template>
  <ToastNotifs ref="toaster" />
  <div v-cloak class="container mx-auto">
    <h2 class="maintitle">
      {{ gameSession.gameType }}
    </h2>
    <div class="flex portrait:flex-col content-center">
      <div id="myAvatar" class="my-4 mx-auto">
        <avatarCard :show-name="false" :avatar-name="gameSession.myName" />
      </div>

      <div class="grow">
        <div class="flex-col">
          <button
            v-if="mainActionText"
            type="button"
            class="btn btn-main"
            @click="mainAction"
            v-text="mainActionText"
          />
          <button
            class="btn"
            @click="backToHome(gameSession, router)"
            v-text="T('Change game')"
          />
          <div class="flex grow">
            <button
              type="button"
              :title="T('Click to copy invite link to the clipboard')"
              class="btn"
              @click="copyURL('link')"
            >
              {{ T("Invite") }}
            </button>

            <input
              id="link"
              size="40"
              type="text"
              class="grow shadow appearance-none border rounded shrink py-2 w-64 px-3 text-gray-700 focus:outline-none focus:shadow-outline"
              :value="joinURL"
            />
          </div>
          <QrCode class="m-4 mx-auto rounded-xl" :text="joinURL" />
        </div>
      </div>

      <div class="m-2 rounded-xl container shadow bg-slate-400 lg:w-1/3 shrink">
        <playerList
          ref="playerlist"
          :players="gameSession.players"
          :enable-kick="
            !states.hasVoted &&
            gameSession.players.length > kick_player_threshold
          "
          :kick-text="T('Kick player')"
          :my-id="gameSession.myId"
          @kick="kickPlayerVote"
        />
      </div>
    </div>
  </div>
</template>

<style scoped>
#myAvatar {
  z-index: 1;
}
#myAvatar:deep(svg) {
  background-color: white;
  border-radius: 1000px;
  transition-duration: 300ms;
  border: solid 3px #333;
}
</style>
