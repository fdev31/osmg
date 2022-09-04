<script setup>
import { onMounted } from "vue";

import { GameSession } from "@/stores/gamesession.js";
import { HighScores } from "@/stores/highscores.js";
import { getTranslation as T, initLocales } from "@/lib/utils.js";

import avatarCard from "@/components/avatarCard.vue";
import ToastNotifs from "@/components/ToastNotifs.vue";

const highScores = HighScores();
const gameSession = GameSession();

document.debug = import.meta.env.DEV ? { gameSession } : {};

initLocales();

onMounted(() => {
  gameSession.started = false;
  gameSession.gameType = false;
  gameSession.save();
});
</script>

<template>
  <ToastNotifs ref="toaster" />
  <h1 class="maintitle">{{ T("HIGH SCORES") }}</h1>
  <div
    v-cloak
    class="flex flex-row flex-wrap mx-auto container p-5 place-content-center"
  >
    <div class="flex flex-col">
      <div v-for="item in highScores.ranking">
        <avatarCard
          :avatarId="`av-${item}`"
          :avatarName="gameSession.getPlayerInfo(item).name"
          :showName="true"
          :size="highScores.winners.indexOf(item) == -1 ? 'small' : 'big'"
        ></avatarCard>
      </div>
    </div>
  </div>
</template>

<style scoped></style>
