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
import { colors } from "@/lib/playercolors.js";

const gameSession = GameSession();
const playerlist = ref();
const grid = ref();
const toaster = ref();
const playersByIndex = gameSession.players.map((o) => o.id);
const myPlayerIndex = computed(() =>
  gameSession.players.indexOf(
    gameSession.players.filter((o) => o.id == gameSession.myId)[0]
  )
);

document.debug = { gameSession };

const UI_CHECKS = false;
initLocales();

const amIplaying = computed(() => {
  return gameSession.gameData.curPlayer == gameSession.myId;
});

function removeFromOthers(reflist, varname, skipId) {
  for (const player of gameSession.players) {
    if (player.id == skipId) continue;
    const davar = gameSession.playersData[player.id][varname];
    gameSession.playersData[player.id][varname] = davar.filter(
      (o) => reflist.indexOf(o) == -1
    );
  }
}

function pText2Int(txt) {
  const [x, y] = txt.split("-");
  return [parseInt(x), parseInt(y)];
}

function generateZoneCoords(x, y) {
  const MAX_BOARD_INDEX = 6;
  const ret = [];
  for (let lx = x - 1; lx < x + 2; lx++) {
    if (lx < 0 || lx > MAX_BOARD_INDEX) continue;
    for (let ly = y - 1; ly < y + 2; ly++) {
      if (ly < 0 || ly > MAX_BOARD_INDEX) continue;
      ret.push(`${lx}-${ly}`);
    }
  }
  return ret;
}

const MAX_BOARD_INDEX = 6;
const BOARD_COORDS = [];
for (let x = 0; x <= MAX_BOARD_INDEX; x++)
  for (let y = 0; y <= MAX_BOARD_INDEX; y++) BOARD_COORDS.push(`${x}-${y}`);

const handlers = {
  curPlayer(data) {
    gameSession.gameData.curPlayer = data.val;
    gameSession.save();
  },
  endOfGame(data) {
    if (data.player === gameSession.myId) {
      toaster.value.show(`You are the winner !!`, { sticky: true });
    } else {
      const winner = gameSession.getPlayerInfo(data.player).name;
      toaster.value.show(`Game Over.\n${winner} Wins!`, { sticky: true });
    }
  },
  varUpdate(data) {
    if (data.val && data.var) {
      for (const pid of Object.keys(data.val)) {
        switch (data.var) {
          case "pawns":
            if (pid == "void") {
              removeFromOthers(data.val[pid], data.var);
            } else {
              removeFromOthers(data.val[pid], data.var, pid);
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
      const freePawns = new Set(BOARD_COORDS);
      for (const pid of gameSession.players) {
        const pd = gameSession.playersData[pid.id];
        if (pd.pawns) {
          for (const pawn of pd.pawns) freePawns.delete(pawn);
        } else {
          console.debug(
            `No pawns for player ${pid} in ${gameSession.playersData}`
          );
        }
      }
      // now we really only have free pawns
      const myPawns = new Set(gameSession.playersData[gameSession.myId].pawns);
      let canIplay = false;
      const checkedCoords = new Set();
      for (const pawn of freePawns) {
        if (canIplay) break;
        const options = generateZoneCoords(...pText2Int(pawn)).filter(
          (o) => !checkedCoords.has(o)
        );
        for (const coord of options) {
          checkedCoords.add(coord);
          if (myPawns.has(coord)) {
            canIplay = true;
            break;
          }
        }
      }
      if (!canIplay) {
        server.surrender();
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
  if (UI_CHECKS && !amIplaying.value) {
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
  async surrender() {
    const obj = getPlayerFromSession(gameSession);
    return await post("/g/atakks/surrender", obj);
  },
};
</script>

<template>
  <Toast ref="toaster" />
  <h1 class="maintitle">
    {{ T("Atakks, a game of mind") }}
  </h1>
  <div v-cloak class="flex flex-row flex-wrap mx-auto container p-5">
    <div
      id="myAvatar"
      :class="{
        playing: amIplaying,
        flex: true,
        'flex-1': true,
        'flex-col': true,
        'items-center': true,
        container: true,
      }"
    >
      <div
        class="p-3 m-3 rounded-full"
        :style="`background-color: ${colors[myPlayerIndex]}`"
      >
        <avatarCard :show-name="false" :avatar-name="gameSession.myName" />
      </div>
    </div>
    <div class="rounded-xl overflow-hidden">
      <atakksGrid
        ref="grid"
        :players-data="gameSession.playersData"
        :players-ids="playersByIndex"
        @pawn-click="handleClick"
      />
    </div>
    <div class="w-30 flex-none bg-slate-400 mx-3 px-2 rounded-xl">
      <playerList
        ref="playerlist"
        :enable-kick="false"
        :kick-text="T('Kick player')"
        :cur-player="gameSession.gameData.curPlayer"
        :players="gameSession.players"
        :my-id="gameSession.myId"
      />
    </div>
  </div>
</template>

<style scoped>
#myAvatar:deep(svg) {
  background-color: white;
  border-radius: 1000px;
  border: solid 3px #333;
  transition-duration: 300ms;
}
#myAvatar.playing:deep(svg) {
  background-color: #d6ffe5;
  border: solid 3px #333;
}
.gameGrid {
  margin: 1em;
  border-radius: 10px;
}
</style>
