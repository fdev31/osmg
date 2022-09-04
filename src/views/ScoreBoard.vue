<script setup>
import { onMounted, onUnmounted } from "vue";

import { GameSession } from "@/stores/gamesession.js";
import { HighScores } from "@/stores/highscores.js";
import {
  getTranslation as T,
  initLocales,
  getPlayerFromSession,
  setupStreamEventHandler,
  post,
} from "@/lib/utils.js";

import avatarCard from "@/components/avatarCard.vue";
import ToastNotifs from "@/components/ToastNotifs.vue";
import router from "../router";

const highScores = HighScores();
const gameSession = GameSession();
let stream;

document.debug = import.meta.env.DEV ? { gameSession } : {};

initLocales();

onUnmounted(() => {
  stream.close();
});

const handlers = {
  restart(data) {
    gameSession.gameType = data.game;
    gameSession.started = false;
    Object.assign(gameSession.gameData, data.gameData);
    for (const plr of Object.keys(gameSession.playersData)) {
      const pi = data.playersData[plr];
      if (pi) Object.assign(gameSession.playersData[plr], pi);
    }
    gameSession.save();
    router.push(`/lobby`);
  },
};

async function restart() {
  const obj = getPlayerFromSession(gameSession);
  await post("/c/session/restart", obj);
}

onMounted(() => {
  stream = setupStreamEventHandler(
    { topic: gameSession.name, uid: gameSession.myId },
    handlers
  );
  gameSession.started = false;
  gameSession.gameType = false;
  gameSession.save();
});
</script>

<template>
  <ToastNotifs ref="toaster" />
  <h1 class="maintitle">
    {{ T("HIGH SCORES") }}
  </h1>
  <div
    v-cloak
    class="flex flex-row flex-wrap mx-auto container p-5 place-content-center"
  >
    <div class="flex flex-col">
      <button class="btn btn-main" @click="restart">Restart</button>
      <div v-for="item in highScores.ranking" :key="item">
        <avatarCard
          :avatar-id="`av-${item}`"
          :avatar-name="gameSession.getPlayerInfo(item).name"
          :show-name="true"
          :size="highScores.winners.indexOf(item) == -1 ? 'small' : 'big'"
        />
      </div>
    </div>
  </div>
</template>

<style scoped></style>
