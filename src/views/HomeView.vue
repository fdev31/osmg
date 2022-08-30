<script setup>
import { onMounted, onUnmounted, ref, watch } from "vue";
import avatarCard from "@/components/avatarCard.vue";
import { useRouter, RouterLink } from "vue-router";
import { GameSession } from "@/stores/gamesession.js";
import { getTranslation as T, initLocales } from "@/lib/utils.js";
import { gamelist } from "@/lib/gamelist.js";
import { makeName } from "@/lib/wordsMaker.js";

const router = useRouter();
const gameSession = GameSession();
const mynickname = ref("Ninon");
const games = ref({});
const avatar = ref();

document.debug = { gameSession };

let namesTimer = null;

initLocales();

watch(mynickname, (newVal) => {
  if (newVal) avatar.value.setName(newVal);
});

function clearTimers() {
  if (namesTimer) clearInterval(namesTimer);
}

onUnmounted(clearTimers);

onMounted(async () => {
  const router = useRouter();
  await router.isReady();
  mynickname.value = makeName();
  games.value = gamelist;
  namesTimer = setInterval(() => {
    mynickname.value = makeName();
  }, 5000);
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
  const response_player = await fetch("/c/session/join", {
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
    gameSession.$patch(result);
    console.log(gameSession.asObject());
    gameSession.save();
    router.push("/lobby");
  } else {
    const result = await response_player.json();
    alert(result.detail);
  }
}

async function clear_session() {
  // TODO: leave existing game first !!
  gameSession.$reset();
  gameSession.save();
  router.push("/");
}

defineExpose({ clear_session, join_game });

async function start_game(game) {
  var response = await fetch(`/c/session/new?gameType=${game}`, {
    method: "GET",
    redirect: "follow",
  });
  let result = await response.json();
  await join_game(result.name);
}
</script>

<template>
  <main v-cloak>
    <div class="bg">
      <div class="container">
        <div class="avatarframe">
          <h2 class="title">{{ T("Identity") }}:</h2>
          <input
            v-model="mynickname"
            type="text"
            placeholder="Nickname"
            maxlength="20"
            @focus="clearTimers()"
          />
          <avatarCard
            ref="avatar"
            noname
            avatar-name="Nick"
            style="margin: -36px 0 0 220px"
            class="avatar"
          />
        </div>
      </div>
      <div v-if="gameSession.name">
        <div v-if="!gameSession.secret">
          <button @click="join_game(gameSession.name)">
            {{ T("Join game") }}
          </button>
        </div>
        <div v-else>
          <RouterLink :to="`game-${gameSession.gameType}`">
            {{ T("Return to game") }}
          </RouterLink>
        </div>
        <button @click="clear_session()">
          {{ T("Change game") }}
        </button>
      </div>
      <div v-else>
        <h1>{{ T("Pick a game") }}:</h1>
        <div class="wrap">
          <div v-for="(info, game) in games" :key="game" class="gamebutton">
            <div class="tile">
              <span @click="start_game(game)">
                <img :src="`/img/${info.card}.jpg`" />
                <div class="text">
                  <h1>{{ T(game) }}</h1>
                  <h2 class="animate-text">{{ T(game + "_description") }}</h2>
                  <div
                    class="animate-text"
                    v-text="T(game + '_long_description')"
                  /></div
              ></span>
            </div>
          </div>
        </div>
      </div>
    </div>
  </main>
</template>

<style scoped>
.avatar {
  position: relative;
  margin: -110px 0 0 294px;
}
.avatarframe {
  background-color: rgb(0 125 152);
  border-radius: 20px;
  height: 395px;
  padding-left: 10%;
}
.avatar svg {
  width: 180px;
  height: 230px;
  display: block;
}
.tile .text {
  height: 3em;
  transition-duration: 1s;
  overflow: hidden;
}
.tile:hover .text {
  height: 10em;
}
input {
  width: 300px;
  height: 33px;
  margin-left: -5%;
  margin-top: 5%;
  padding: 3px;
  border-radius: 5px;
  border: 0px;
  transition: 0.4s ease-in-out;
  z-index: 2;
}

input:hover {
  transform: scale(1.05, 1.05);
}

input:focus {
  color: #151515;
  font-family: "Josefin Sans", sans-serif;
  font-size: 18px;
  outline: none;
  padding-left: 10px;
  border-left: 5px solid #00a4ff;
}
text {
  pointer-events: none;
  overflow: hidden;
}

.wrap {
  margin: 50px auto 0 auto;
  width: 100%;
  display: grid;
  align-items: space-around;
  max-width: 1200px;
  cursor: pointer;
}
.gamebutton {
  background-color: #3e434b;
  width: 64%;
  margin-left: 18%;
  border-radius: 10px;
  padding: 1em;
  margin-bottom: 2em;
}
div.tile > span > img {
  width: 100%;
  border-radius: 10px;
}
</style>
