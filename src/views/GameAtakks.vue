<script setup>
import { ref, onMounted, watchEffect } from "vue";

import { GameSession } from "@/stores/gamesession.js";
import {
  getTranslation as T,
  initLocales,
  setupStreamEventHandler,
} from "@/lib/utils.js";

import playerList from "@/components/playerList.vue";
import atakksGrid from "@/components/atakksGrid.vue";

const gameSession = GameSession();
for (const player of gameSession.players) {
  player.ready = false; // reset lobby state
}
const playerlist = ref();

initLocales();

const handlers = {};

onMounted(() => {
  setupStreamEventHandler(
    { topic: gameSession.name, uid: gameSession.myId },
    handlers
  );
});
</script>

<template>
  <div v-cloak>
    <h1>{{ T("Attaks, a game of mind") }}</h1>
    <div id="players_frame">
      <playerList
        id="playersContainer"
        ref="playerlist"
        :enable-kick="false"
        :kick-text="T('Kick player')"
        :cur-player="gameSession.gameData.curPlayer"
        :players="gameSession.players"
        :my-id="gameSession.myId"
      />
    </div>
    <atakksGrid :players-data="gameSession.playersData" />
  </div>
</template>

<style scoped>
#players_frame {
  position: fixed;
  padding: 1ex 2ex;
  right: 1em;
  display: block;
  border: solid 2px grey;
  border-radius: 10px;
  background-color: rgba(0, 0, 0, 0.5);
  display: block;
  inline-size: fit-content;
}
@media (max-width: 1024px) {
  #players_frame {
    left: 1em;
    clear: both;
    display: block;
    position: relative;
    margin: 0;
  }
}
</style>
