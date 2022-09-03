<script setup>
import { ref, onMounted, onUnmounted, computed } from "vue";
import { GameSession } from "@/stores/gamesession.js";

import ToastNotifs from "@/components/ToastNotifs.vue";
import playerList from "@/components/playerList.vue";
import DiceArray from "@/components/DiceArray.vue";
import avatarCard from "@/components/avatarCard.vue";

import { kickPlayerVote } from "@/lib/voting.js";

import {
  getTranslation as T,
  initLocales,
  getPlayerFromSession,
  host,
  post,
  getLogger,
  setupStreamEventHandler,
} from "@/lib/utils.js";

const log = getLogger("marathon");
const gameSession = GameSession();
const toaster = ref();
const playerlist = ref();
const mydice = ref();

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

const ui = gameSession.uiStates;

const kick_player_threshold = 2;

onMounted(() => {
  if (ui.status == undefined) {
    ui.status = statuses.UNINITIALIZED;
  } else if (ui.currentThrow) {
    mydice.value.updateDice(ui.currentThrow, false);
    mydice.value.enableDrag(true);
  } else if (isMyTurn) {
    mydice.value && mydice.value.updateDice([0, 0, 0, 0], false);
  }
});

function isError(res) {
  return res && res.detail != undefined;
}

function checkLost() {
  if (gameSession.playersData[gameSession.myId].distance < 0) {
    ui.status = statuses.GAME_OVER;
    gameSession.save();
    return true;
  }
}
const handlers = {
  curPlayer: (data) => {
    if (!checkLost()) {
      gameSession.gameData.curPlayer = data.val;
      if (data.val === gameSession.myId) {
        ui.status = statuses.THROW;
        gameSession.save();
        setTimeout(() => {
          mydice.value.updateDice([0, 0, 0, 0], false);
          mydice.value.diceNumber = Math.min(
            4,
            ("" + (gameSession.playersData[gameSession.myId].distance - 1))
              .length
          );
        }, 1);
        toaster.value.show(T("It's your turn to play!"), {
          closeTimeOut: 3500,
        });
      }
    }
    gameSession.save();
  },
  connectPlayer: (data) => {
    gameSession.playersData[data.id].disconnected = false;
    toaster.value.show(
      `${gameSession.getPlayerInfo(data.id).name} ${T("enters the game")}`
    );
    gameSession.save();
  },
  disconnectPlayer: (data) => {
    gameSession.playersData[data.id].disconnected = true;
    toaster.value.show(
      `${gameSession.getPlayerInfo(data.id).name} ${T("is disconnected")}`
    );
    gameSession.save();
  },
  varUpdate: (data) => {
    if (data.player) {
      let pd = gameSession.playersData[data.player];
      if (pd === undefined) {
        pd = gameSession.playersData[data.player] = {};
      }
      if (data.player != gameSession.myId) {
        toaster.value.show(
          `${gameSession.getPlayerInfo(data.player).name} ${T("moved")} ${
            parseInt(gameSession.playersData[data.player].distance) -
            parseInt(data.val)
          } ${T("meters")}`
        );
      }
      gameSession.playersData[data.player].distance = data.val;
    } else {
      gameSession.gameData[data.var] = data.val;
    }
    gameSession.save();
    checkLost();
  },
  newTurn: (data) => {
    checkLost();
    gameSession.gameData.turns = data.val;
  },
  endOfGame: (data) => {
    let message = data.message;
    let myStatus = statuses.GAME_OVER;
    for (let player of gameSession.players) {
      if (player.id == data.player) {
        message += "\nPlayer " + player.name + " wins!";
        if (player.id == gameSession.myId) myStatus = statuses.GAME_WON;
      }
    }
    toaster.value.show(message, { sticky: true });
    ui.status = myStatus;
    gameSession.gameData.turn = 0;
    gameSession.save();
    // TODO: move to end of game
  },
};

const isLastAction = computed(() => statuses.DICE_THROWN == ui.status);
const isMyTurn = computed(
  () => gameSession.gameData.curPlayer == gameSession.myId
);
const sortedPlayers = computed(() => {
  const players = gameSession.players.map((o) =>
    Object.assign({}, o, gameSession.playersData[o.id])
  );
  return players.sort((a, b) => a.distance - b.distance);
});

const kickEnabled = computed(
  () =>
    !gameSession.gameData.hasVoted &&
    gameSession.players.length > kick_player_threshold
);

initLocales();

function getPlayerAction() {
  return [
    T("Waiting for other players"),
    T("Throw dices"),
    T("Move forward"),
    T("Wait"),
    T("End of Turn"),
    T("Game won"),
    T("Game"),
    T("Error"),
  ][ui.status];
}

async function mainPlayButton() {
  switch (ui.status) {
    case statuses.THROW:
      await server.throw_dices();
      break;
    case statuses.DICE_THROWN:
      await server.player_advance();
      break;
  }
}

function getPostArg() {
  return {
    id: gameSession.myId,
    secret: gameSession.secret,
    sessionName: gameSession.name,
  };
}

const server = {
  async throw_dices() {
    try {
      let diceValues = await post("/g/marathon/throwDice", getPostArg());
      ui.status = statuses.DICE_THROWN;
      ui.currentThrow = diceValues;

      mydice.value.diceNumber = diceValues.length;
      mydice.value.updateDice(diceValues);
      mydice.value.enableDrag(true);
    } catch (e) {
      toaster.value.show(e.message, { closeTimeOut: 10000 });
      ui.status = statuses.ERROR;
    }
    gameSession.save();
  },
  async skipTurn() {
    await server.player_advance(0);
  },
  async player_advance(value) {
    ui.currentThrow = false;
    let choice =
      value === undefined ? mydice.value.getDiceValues().join("") : value;

    let action = await post(
      `/g/marathon/validateDice?value=${choice}`,
      getPostArg()
    );
    if (isError(action)) {
      alert(action.detail);
    } else {
      ui.status = statuses.END_TURN;
      gameSession.save();
    }
  },
};
function getProgress(id) {
  return (
    100 * ((42195 - gameSession.playersData[`${id}`].distance) / 42195) || 0
  );
}
function showRules() {
  let closeBtn = {
    close: {
      hideOnClick: true,
    },
  };
  toaster.value.show(T("marathon_rules"), {
    closeTimeOut: -1,
    buttonGroup: closeBtn,
  });
}

setupStreamEventHandler(
  { topic: gameSession.name, uid: gameSession.myId },
  handlers
);

document.debug = import.meta.env.DEV ? { gameSession, mydice, server } : {};
</script>

<template>
  <div v-cloak class="container mx-auto">
    <ToastNotifs ref="toaster" />
    <h1 class="font-title">{{ T("Marathon , the dice game") }}</h1>
    <div class="w-96">
      <player-list
        ref="playerlist"
        :enable-kick="kickEnabled"
        kick-text="kick"
        :players="gameSession.players"
        :cur-player="gameSession.gameData.curPlayer"
        :my-id="gameSession.myId"
      />
    </div>
    <div class="flex container items-center">
      <span
        class="m-3 rounded-full"
        :style="`background-color: ${gameSession.getPlayerColor(
          gameSession.myId
        )}`"
      >
        <avatarCard
          size="small"
          :show-name="false"
          :avatar-name="gameSession.myName"
        />
      </span>
      <transition name="fade">
        <div v-if="isMyTurn" class="w-full flex items-center container">
          <div class="mx-5">
            <dice-array ref="mydice" />
          </div>
          <button
            id="playButton"
            type="button"
            class="btn btn-main"
            @click="mainPlayButton"
          >
            {{ getPlayerAction() }}
          </button>
          <button
            v-if="isLastAction"
            type="button"
            class="btn"
            @click="server.skipTurn"
          >
            {{ T("Pass") }}
          </button>
        </div>
      </transition>
    </div>
    <div class="font-bold text-xl">
      {{ T("It's turn").toLowerCase() }}
      {{ parseInt(gameSession.gameData.turns + 1) }}, {{ getPlayerAction() }}:
      <b>
        {{ gameSession.playersData[gameSession.myId].distance }}
      </b>
      {{ T("meters left") }}
    </div>
    <b></b>

    <div>
      <transition-group name="fade">
        <div
          v-for="item in sortedPlayers"
          :key="item.id"
          class="container flex flex-row"
        >
          <span class="w-36 text-right mx-2">{{ item.name }}</span>
          <div class="w-96 bg-gray-200 h-5 mb-6 rounded">
            <div
              class="duration-300 bg-blue-600 h-5 text-xs text-white px-1 text-right rounded"
              :style="`background-color: ${gameSession.getPlayerColor(
                item.id
              )}; width: ${getProgress(item.id)}%`"
            >
              {{ item.distance }}m
            </div>
          </div>
        </div>
      </transition-group>
    </div>

    <div>
      <button class="btn" @click="showRules">{{ T("Show rules") }}</button>
    </div>
  </div>
</template>

<style scoped>
/* 1. declare transition */
.fade-move,
.fade-enter-active,
.fade-leave-active {
  transition: all 0.5s cubic-bezier(0.55, 0, 0.1, 1);
}

/* 2. declare enter from and leave to state */
.fade-enter-from,
.fade-leave-to {
  opacity: 0;
  transform: scaleX(0.01) translate(30px, 0);
}

/* 3. ensure leaving items are taken out of layout flow so that moving
      animations can be calculated correctly. */
.fade-leave-active {
  /* position: absolute; */
}
</style>
