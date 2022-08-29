<script setup>
import { ref, onMounted } from "vue";

import { GameSession } from "@/stores/gamesession.js";
import {
  getTranslation as T,
  initLocales,
  setupStreamEventHandler,
} from "@/lib/utils.js";

import playerList from "@/components/playerList.vue";
import atakksGrid from "@/components/atakksGrid.vue";
import Toast from "@/components/Toast.vue";

const gameSession = GameSession();
const playerlist = ref();
const grid = ref();
const toaster = ref();
const playersByIndex = gameSession.players.map((o) => o.id);
initLocales();

const handlers = {};

onMounted(() => {
  setupStreamEventHandler(
    { topic: gameSession.name, uid: gameSession.myId },
    handlers
  );
});

let pawnToMove;
function handleClick(pos) {
  if (gameSession.gameData.curPlayer != gameSession.myId) {
    toaster.value.show("Not your turn!", { type: "warning", duration: 2000 });
    return;
  }
  if (pos.idx) {
    // there is a player at position
    if (playersByIndex[pos.idx - 1] == gameSession.myId) {
      if (pawnToMove == pos) {
        grid.value.setState("", pos.x, pos.y);
        pawnToMove = undefined;
      } else {
        pawnToMove = pos;
        grid.value.setState("clicked", pos.x, pos.y);
      }
    }
  } else {
    // empty
    if (pawnToMove == undefined) {
      // check surrounding cells to understand if we can add one here
      let valid = false;
      for (let x = -1; x <= 1; x++) {
        for (let y = -1; y <= 1; y++) {
          if (valid) break;
          if (x || y)
            valid = grid.value.getPlayerAtCoordinate(pos.x + x, pos.y + y);
        }
      }
      if (valid) {
        gameSession.playersData[gameSession.myId]["pawns"].push(
          `${pos.x}-${pos.y}`
        );
      }
    } else {
      if (
        pos.x >= pawnToMove.x - 2 &&
        pos.x <= pawnToMove.x + 2 &&
        pos.y >= pawnToMove.y - 2 &&
        pos.y <= pawnToMove.y + 2
      ) {
        const toBeRemoved = `${pawnToMove.x}-${pawnToMove.y}`;
        const newList = gameSession.playersData[gameSession.myId][
          "pawns"
        ].filter((o) => o != toBeRemoved);
        newList.push(`${pos.x}-${pos.y}`);
        gameSession.playersData[gameSession.myId]["pawns"] = newList;
        grid.value.setState("", pawnToMove.x, pawnToMove.y);
        pawnToMove = undefined;
      }
    }
  }
}
</script>

<template>
  <Toast ref="toaster" />
  <div v-cloak>
    <h1>{{ T("Attaks, a game of mind") }}</h1>
    <div id="players_frame">
      <playerList
        ref="playerlist"
        :enable-kick="false"
        :kick-text="T('Kick player')"
        :cur-player="gameSession.gameData.curPlayer"
        :players="gameSession.players"
        :my-id="gameSession.myId"
      />
    </div>
    <atakksGrid
      ref="grid"
      @pawnClick="handleClick"
      class="gameGrid"
      :players-data="gameSession.playersData"
      :players-ids="playersByIndex"
    />
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
.gameGrid {
  margin: 1em;
  border-radius: 10px;
}
</style>
