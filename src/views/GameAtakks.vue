<script setup>
import { ref, onMounted, onUnmounted, computed } from "vue";

import { GameSession } from "@/stores/gamesession.js";
import {
  getTranslation as T,
  initLocales,
  getPlayerFromSession,
  post,
  setupStreamEventHandler,
} from "@/lib/utils.js";

import playerList from "@/components/playerList.vue";
import atakksGrid from "@/components/atakksGrid.vue";
import avatarCard from "@/components/avatarCard.vue";
import Toast from "@/components/Toast.vue";

const gameSession = GameSession();
const playerlist = ref();
const grid = ref();
const toaster = ref();
const playersByIndex = gameSession.players.map((o) => o.id);

const UI_CHECKS = false;
initLocales();

const amIplaying = computed(() => {
  return gameSession.gameData.curPlayer == gameSession.myId;
});

const handlers = {
  curPlayer(data) {
    gameSession.gameData.curPlayer = data.val;
    gameSession.save();
  },
  varUpdate(data) {
    if (data.val && data.var) {
      for (const pid of Object.keys(data.val)) {
        switch (data.var) {
          case "pawns":
            if (pid == "void") {
              // remove those references on other players
              const reflist = data.val[pid];
              for (const player of gameSession.players) {
                const davar = gameSession.playersData[player.id][data.var];
                gameSession.playersData[player.id][data.var] = davar.filter(
                  (o) => reflist.indexOf(o) == -1
                );
              }
            } else {
              // just append new positions
              const davar = gameSession.playersData[pid][data.var];
              for (const val of data.val[pid]) {
                davar.push(val);
              }
            }
            break;
          default:
            console.debug("Don't know how to update " + data.var);
        }
      }
    }
    gameSession.save();
  },
};

let stream;

onMounted(() => {
  stream = setupStreamEventHandler(
    { topic: gameSession.name, uid: gameSession.myId },
    handlers
  );
});

onUnmounted(() => {
  stream.close();
});

let pawnToMove;
async function handleClick(pos) {
  if (UI_CHECKS && !amIplaying) {
    toaster.value.show("Not your turn!", { type: "alert", duration: 2000 });
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
            if (
              grid.value.getPlayerAtCoordinate(pos.x + x, pos.y + y) ==
              gameSession.myId
            ) {
              valid = { x: pos.x + x, y: pos.y + y };
            }
        }
      }
      if (valid) {
        const ret = await server.add(pos, valid);
        if (ret.detail) toaster.value.show(ret.detail, { type: "alert" });
      } else {
        toaster.value.show("Invalid move.", { duration: 2000 });
      }
    } else {
      if (
        pos.x >= pawnToMove.x - 2 &&
        pos.x <= pawnToMove.x + 2 &&
        pos.y >= pawnToMove.y - 2 &&
        pos.y <= pawnToMove.y + 2
      ) {
        const ret = await server.move(pos, pawnToMove);
        if (ret.detail) toaster.value.show(ret.detail, { type: "alert" });
        grid.value.setState("", pawnToMove.x, pawnToMove.y);
        pawnToMove = undefined;
      } else {
        toaster.value.show("Invalid move.", { duration: 2000 });
      }
    }
  }
}
const server = {
  async add(pawn, reference) {
    const obj = {
      player: getPlayerFromSession(gameSession),
      reference: { x: reference.x, y: reference.y },
      position: { x: pawn.x, y: pawn.y },
    };
    return await post("/g/atakks/add", obj);
  },
  async move(pawn, from) {
    const obj = {
      player: getPlayerFromSession(gameSession),
      source: { x: from.x, y: from.y },
      destination: { x: pawn.x, y: pawn.y },
    };
    return await post("/g/atakks/move", obj);
  },
};
</script>

<template>
  <Toast ref="toaster" />
  <div v-cloak>
    <h1>{{ T("Atakks, a game of mind") }}</h1>
    <div
      id="myAvatar"
      :class="{
        playing: amIplaying,
      }"
    >
      <avatarCard :show-name="false" :avatar-name="gameSession.myName" />
    </div>
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
#myAvatar {
  float: right;
  margin-top: -64px;
  height: 2em;
}
#myAvatar:deep(svg) {
  background-color: white;
  border-radius: 1000px;
  transition-duration: 300ms;
}
#myAvatar.playing:deep(svg) {
  background-color: #d5680f;
  border: solid 3px #333;
}
@media (min-width: 1024px) {
  @media (max-width: 1600px) {
    #myAvatar {
      margin-right: 200px;
    }
  }
}
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
