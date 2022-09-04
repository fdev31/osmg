<script setup>
import { onMounted, onUnmounted, ref, watch } from "vue";
import avatarCard from "@/components/avatarCard.vue";
import { useRouter, RouterLink } from "vue-router";
import { GameSession } from "@/stores/gamesession.js";
import { getTranslation as T, initLocales, host } from "@/lib/utils.js";
import { gamelist } from "@/lib/gamelist.js";
import { makeName } from "@/lib/wordsMaker.js";
import { backToHome } from "@/lib/session";

const gameSession = GameSession();
const router = useRouter();
const games = ref({});
const avatar = ref();
const mynickname = ref();

document.debug = import.meta.env.DEV ? { gameSession } : {};

let namesTimer = null;

initLocales();

watch(mynickname, (newVal) => {
  if (newVal) avatar.value.setName(newVal);
});

function clearTimers() {
  if (namesTimer) {
    clearInterval(namesTimer);
    gameSession.namePicked = mynickname.value;
  }
}

onUnmounted(clearTimers);

onMounted(async () => {
  const router = useRouter();
  await router.isReady();
  mynickname.value = gameSession.namePicked || makeName();
  if (!gameSession.namePicked) {
    namesTimer = setInterval(() => {
      mynickname.value = makeName();
    }, 5000);
  }
  games.value = gamelist;
});

async function join_game(sessionId) {
  // create a standard player for creator of session game
  const myHeaders = new Headers();
  myHeaders.append("Content-Type", "application/json");
  var raw = JSON.stringify({
    name: mynickname.value,
    avatar: "",
    sessionName: sessionId || gameSession.name,
  });
  const response_player = await fetch(`${host}/c/session/join`, {
    method: "POST",
    redirect: "follow",
    headers: myHeaders,
    body: raw,
  });
  if (response_player.status == 200) {
    const result = await response_player.json();
    for (let player of result.players) {
      if (player.name == mynickname.value) result.myId = player.id;
    }
    gameSession.namePicked = mynickname.value;
    gameSession.$patch(result);
    gameSession.save();
    router.push("/lobby");
  } else {
    const result = await response_player.json();
    alert(result.detail);
  }
}

async function start_game(game) {
  var response = await fetch(`${host}/c/session/new?gameType=${game}`, {
    method: "GET",
    redirect: "follow",
  });
  let result = await response.json();
  await join_game(result.name);
}
</script>

<template>
  <main v-cloak class="flex flex-col content-start items-center m-5">
    <div class="items-center">
      <avatarCard
        ref="avatar"
        noname
        avatar-name="Nick"
        class="bg-sky-300 bg-opacity-50 w-max rounded-full mx-auto shadow-lg"
      />
      <input
        id="username"
        v-model="mynickname"
        type="text"
        placeholder="Nickname"
        maxlength="20"
        class="text-center shadow-lg appearance-none border rounded w-full py-2 px-3 text-gray-700 focus:outline-none focus:shadow-outline"
        @focus="clearTimers()"
      />
    </div>
    <div v-if="!gameSession.secret && gameSession.name" class="contents w-full">
      <button class="btn w-48 btn-main" @click="join_game(gameSession.name)">
        {{ T("Join game") }}
      </button>
    </div>
    <div v-if="gameSession.secret && gameSession.name" class="contents w-full">
      <RouterLink
        v-if="gameSession.gameType"
        :to="`game-${gameSession.gameType}`"
        class="btn btn-main block w-48"
      >
        {{ T("Return to game") }}
      </RouterLink>
      <button class="btn w-48" @click="backToHome(gameSession, router)">
        {{ T("Change game") }}
      </button>
    </div>
    <div v-if="!gameSession.name" class="basis">
      <div class="font-title text-center m-10">{{ T("Select a game") }}:</div>
      <div class="grid xl:grid-cols-3 md:grid-cols-2 sm:grid-cols-1 gap-1">
        <div
          v-for="(info, game) in games"
          :key="game"
          class="tile cursor-pointer group tileshadow-md rounded-xl max-w-md mx-auto flex flex-initial flex-col duration-300"
          @click="start_game(game)"
        >
          <img
            :src="`/img/hometiles/${info.card}.jpg`"
            class="shadow-lg object-fill h-96 w-96 rounded-xl md:w-full"
          />
          <div class="font-title">
            {{ T(game) }}
          </div>
          <div
            class="shadow-xl opacity-0 group-hover:opacity-100 text-black duration-300 bg-slate-200 rounded-md px-2 overflow-clip"
          >
            <h2 class="animate-text">
              {{ T(game + "_description") }}
            </h2>
            <div class="animate-text" v-html="T(game + '_long_description')" />
          </div>
        </div>
      </div>
    </div>
  </main>
</template>

<style scoped></style>
