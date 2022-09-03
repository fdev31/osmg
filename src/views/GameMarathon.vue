<script setup>
import { ref, onMounted, onUnmounted, computed } from "vue";
import { GameSession } from "@/stores/gamesession.js";

import ToastNotifs from "@/components/ToastNotifs.vue";
import playerList from "@/components/playerList.vue";
import DiceArray from "@/components/DiceArray.vue";

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

document.debug = import.meta.env.DEV ? { gameSession, mydice } : {};

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
  },
  connectPlayer: (data) => {
    gameSession.playersData[data.id].disconnected = false;
    toaster.value.show(
      `${gameSession.getPlayerInfo(data.id).name} ${T("enters the game")}`
    );
  },
  disconnectPlayer: (data) => {
    gameSession.playersData[data.id].disconnected = true;
    toaster.value.show(
      `${gameSession.getPlayerInfo(data.id).name} ${T("is disconnected")}`
    );
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
      animateProgressBar(data.player, pd.distance, data.val);
    } else {
      gameSession.gameData[data.var] = data.val;
    }
    checkLost();
  },
  newTurn: (data) => {
    checkLost();
    gameSession.gameData.turn = data.val;
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
const diceVisible = computed(() =>
  [statuses.THROW, statuses.DICE_THROWN].includes(ui.status)
);
const sortedPlayers = computed(() => {
  let data = gameSession.playersData;
  let result = [];
  Object.keys(data).map(function (key) {
    return result.push([key, data[key]]);
  });
  result = result
    .sort(function (a, b) {
      return a[1].distance - b[1].distance;
    })
    .map((x) => {
      return Object.assign(gameSession.getPlayerInfo(x[0]), x[1]);
    });
  return result;
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

      mydice.value.diceNumber = diceValues.length;
      mydice.value.updateDice(diceValues);
      mydice.value.enableDrag(true);
    } catch (e) {
      toaster.value.show(e.message, { closeTimeOut: 10000 });
      ui.status = statuses.ERROR;
    }
  },
  async skipTurn() {
    await server.player_advance(0);
  },
  async player_advance(value) {
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
    }
  },
};
function getProgress(id) {
  return (
    100 * ((42195 - gameSession.playersData[`${id}`].distance) / 42195) || 0
  );
}
function animateProgressBar(id, start, stop, fps = 120) {
  let distInterval = Math.ceil((start - stop) / 20);
  let intervalId = setInterval(() => {
    gameSession.playersData[`${id}`].distance -= distInterval;
    if (gameSession.playersData[`${id}`].distance < stop) {
      clearInterval(intervalId);
      gameSession.playersData[`${id}`].distance = stop;
    }
  }, Math.floor(3600 / fps));
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

if (gameSession.gameData.turns == 0) {
  for (const key in gameSession.playersData) {
    if (Object.hasOwnProperty.call(gameSession.playersData, key)) {
      gameSession.playersData[key].distance = 42195;
    }
  }
}
</script>

<template>
  <div v-cloak>
    <ToastNotifs ref="toaster" />
    <h1>{{ T("Marathon , the dice game") }}</h1>
    <player-list
      ref="playerlist"
      :enable-kick="kickEnabled"
      kick-text="kick"
      :players="gameSession.players"
      :cur-player="gameSession.gameData.curPlayer"
      :my-id="gameSession.myId"
    />
    <h2>
      {{ T("Welcome") }} {{ gameSession.getPlayerInfo(gameSession.myId).name }},
      {{ T("It's turn").toLowerCase() }}
      {{ parseInt(gameSession.gameData.turns + 1) }}
    </h2>
    <div v-if="ui.status == statuses.GAME_WON">
      <h1>{{ T("You Win") }}!</h1>
    </div>
    <div v-else-if="ui.status == statuses.GAME_OVER">
      <h1>{{ T("You Lose") }}!</h1>
    </div>
    <div v-else>
      <div>
        <b>{{ getPlayerAction() }}</b>
      </div>
      {{ gameSession.playersData[gameSession.myId].distance }}
      {{ T("meters left") }}
      <button
        v-if="diceVisible"
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
      <transition name="fade">
        <div v-if="diceVisible" class="diceArea">
          <dice-array ref="mydice" />
        </div>
      </transition>
    </div>

    <div class="marathon-rank">
      <transition-group name="flip-list">
        <div v-for="item in sortedPlayers" :key="item.name" class="player">
          <span class="name">{{ item.name }}</span>
          <span> <progress max="100" :value="getProgress(item.id)" /> </span
          ><span> {{ item.distance }} {{ T("meters") }}</span>
        </div>
      </transition-group>
    </div>

    <div>
      <button class="btn" @click="showRules">Voir les règles</button>
    </div>
  </div>
</template>

<style></style>
