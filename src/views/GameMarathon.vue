<script setup>
import { ref, onMounted, onUnmounted, computed, watch } from "vue";
import { useRouter } from "vue-router";
import { GameSession } from "@/stores/gamesession.js";
import { HighScores } from "@/stores/highscores.js";

import ToastNotifs from "@/components/ToastNotifs.vue";
import playerList from "@/components/playerList.vue";
import DiceArray from "@/components/DiceArray.vue";
import avatarCard from "@/components/avatarCard.vue";

import {
  getTranslation as T,
  initLocales,
  post,
  setupStreamEventHandler,
} from "@/lib/utils.js";

const router = useRouter();
const gameSession = GameSession();
const highScores = HighScores();
const toaster = ref();
const playerlist = ref();
const mydice = ref();

const statuses = {
  UNINITIALIZED: 0,
  THROW: 1,
  DICE_THROWN: 2,
  END_TURN: 3,
  GAME_OVER: 4,
  GAME_WON: 5,
  ERROR: 6,
};

watch(router.currentRoute, () => {
  toaster.value.clearAll();
});

const ui = gameSession.uiStates;

const kick_player_threshold = 2;

let stream;

onMounted(() => {
  if (ui.status == undefined) {
    ui.status = statuses.UNINITIALIZED;
  }
  if (ui.currentThrow) {
    mydice.value.updateDice(ui.currentThrow, false);
    mydice.value.enableDrag(true);
  } else if (isMyTurn.value) {
    mydice.value && mydice.value.updateDice([0, 0, 0, 0], false);
  }
});

function isError(res) {
  return res && res.detail != undefined;
}

function checkLost() {
  if (gameSession.playersData[gameSession.myId].distance < 0) {
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
          mydice.value.diceNumber = Math.min(
            4,
            ("" + (gameSession.playersData[gameSession.myId].distance - 1))
              .length
          );
          mydice.value.updateDice([0, 0, 0, 0], false);
        }, 1);
        toaster.value.show(T("It's your turn to play!"), {
          duration: 1000,
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
    gameSession.save();
  },
  endOfGame: (data) => {
    ui.gameEnded = true;
    let message = data.message;
    let plr = gameSession.getPlayerInfo(data.player);
    if (plr.id == gameSession.myId) {
      message += "\nAnd YOU are the winner!";
      ui.status = statuses.GAME_WON;
    } else {
      message += "\nPlayer " + plr.name + " wins!";
      ui.status = statuses.GAME_OVER;
    }
    toaster.value.show(message, { sticky: true });
    gameSession.save();
    highScores.ranking = sortedPlayers.value.map((o) => o.id);
    highScores.winners = [plr.id];
    setTimeout(() => {
      router.push("/scoreboard");
    }, 3000);
  },
};

const isMyTurn = computed(
  () => gameSession.gameData.curPlayer == gameSession.myId
);
const positiveOrDie = (i) => (i > 0 ? i : 99999 - i);

const sortedPlayers = computed(() => {
  const players = gameSession.players.map((o) =>
    Object.assign({}, o, gameSession.playersData[o.id])
  );
  return players.sort(
    (a, b) => positiveOrDie(a.distance) - positiveOrDie(b.distance)
  );
});

const kickEnabled = computed(
  () =>
    !gameSession.gameData.hasVoted &&
    gameSession.players.length > kick_player_threshold
);

const currentActionName = computed(
  () =>
    [
      T("waiting for other players"),
      T("throw dices"),
      T("move forward"),
      T("wait for your turn"),
      T("game over"),
      T("game won"),
      T("error"),
    ][ui.status]
);

initLocales();

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
      toaster.value.show(e.message, { duration: 10000 });
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
  toaster.value.show(T("marathon_rules"), { sticky: true });
}

onMounted(() => {
  highScores.$reset();
  stream = setupStreamEventHandler(
    { topic: gameSession.name, uid: gameSession.myId },
    handlers
  );
});

onUnmounted(() => {
  stream.close();
});

document.debug = import.meta.env.DEV
  ? { gameSession, mydice, server, router }
  : {};
</script>

<template>
  <div v-cloak class="container mx-auto">
    <ToastNotifs ref="toaster" position="bottom-right" />
    <h1 class="maintitle">
      {{ T("Marathon , the dice game") }}
    </h1>
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
        class="m-3 rounded-full overflow-hidden flex-none"
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
        <div
          v-if="isMyTurn && !ui.gameEnded"
          class="w-full flex items-center container"
        >
          <div class="mx-5">
            <dice-array ref="mydice" />
          </div>
          <button
            v-if="isMyTurn && !ui.currentThrow"
            id="playButton"
            type="button"
            class="btn btn-main"
            @click="server.throw_dices()"
            v-text="T('Throw')"
          />
          <button
            v-if="isMyTurn && ui.currentThrow"
            id="playButton"
            type="button"
            class="btn btn-main"
            @click="server.player_advance()"
            v-text="T('Confirm')"
          />
          <button
            v-if="statuses.DICE_THROWN == ui.status"
            type="button"
            class="btn"
            @click="server.skipTurn"
          >
            {{ T("Pass") }}
          </button>
        </div>
      </transition>
    </div>
    <div class="font-bold text-xl my-5">
      {{ T("Turn") }}
      {{ parseInt(gameSession.gameData.turns + 1) }}, {{ currentActionName }}:
      <b>
        {{ gameSession.playersData[gameSession.myId].distance }}
      </b>
      {{ T("meters left") }}
    </div>
    <div>
      <transition-group name="fade">
        <div
          v-for="item in sortedPlayers"
          :key="item.id"
          class="container flex flex-row"
        >
          <span class="w-36 text-right mx-2 xl:text-xl">{{ item.name }}</span>
          <div class="w-96 bg-gray-200 h-5 xl:h-10 mb-6 rounded">
            <div
              class="duration-300 bg-blue-600 h-5 xl:h-10 px-1 rounded text-right"
              :style="`background-color: ${gameSession.getPlayerColor(
                item.id
              )}; width: ${getProgress(item.id)}%`"
            >
              <span
                class="bg-slate-900 rounded bg-opacity-50 text-white text-xs xl:text-xl"
                >{{ item.distance }}m</span
              >
            </div>
          </div>
        </div>
      </transition-group>
    </div>

    <div>
      <button class="btn" @click="showRules">
        {{ T("Show rules") }}
      </button>
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
