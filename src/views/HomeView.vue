<script setup>
import { onMounted, onBeforeMount, ref, watch } from "vue";
import avatarCard from "@/components/avatarCard.vue";
import { RouterLink, useRouter } from "vue-router";
import { GameSession } from "@/stores/gamesession.js";

const router = useRouter();

const gameSession = GameSession();

import {
  getJson,
  getTranslation,
  initLocales,
  setCookie,
} from "@/lib/utils.js";

const mynickname = ref("Ninon");
const games = ref({});
const avatar = ref();

watch(mynickname, (newVal) => {
  avatar.value.setName(newVal);
});

const T = getTranslation;

initLocales();
onMounted(async () => {
  const router = useRouter();
  await router.isReady();
  avatar.value.setName(mynickname.value);
  if (!gameSession.name) {
    // no need if not displayed
    games.value = await getJson("/c/gamelist");
  }
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
    setCookie(result);
    router.push("/lobby");
  } else {
    const result = await response_player.json();
    alert(result.detail);
  }
}

async function clear_session() {
  gameSession.$reset();
  games.value = await getJson("/c/gamelist");
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
  <main>
    <div class="bg" v-cloak>
      <h1 class="title">{{ T("Chose a name") }}:</h1>
      <div class="container">
        <div class="avatarframe">
          <input
            v-model="mynickname"
            type="text"
            placeholder="Nickname"
            maxlength="20"
          />
          <avatar-card
            noname
            ref="avatar"
            avatarName="Nick"
            style="margin: -36px 0 0 220px"
            class="avatar"
          >
          </avatar-card>
        </div>
      </div>
      <div v-if="gameSession.name">
        <button @click="join_game(gameSession.name)">
          {{ T("Join game") }}
        </button>
        <button @click="clear_session()">{{ T("Change game") }}</button>
      </div>
      <div v-else>
        <h1>{{ T("Pick a game") }}:</h1>
        <div class="wrap">
          <div v-for="(info, game) in games" class="gamebutton">
            <div class="tile">
              <span @click="start_game(game)">
                <img :src="`/img/${info.card}.jpg`" />
                <div class="text">
                  <h1>{{ T(game) }}</h1>
                  <h2 class="animate-text">{{ T(game + "_description") }}</h2>
                  <p
                    class="animate-text"
                    v-html="T(game + '_long_description')"
                  ></p>
                </div>
              </span>
            </div>
          </div>
        </div>
      </div>
    </div>
  </main>
</template>

<style>
input {
  width: 300px;
  height: 33px;
  margin-left: 8px;
  margin-top: 8px;
  padding: 3px;
  border-radius: 5px;
  border: 0px;
  transition: 0.4s ease-in-out;
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
.avatar {
  position: relative;
}
.avatar svg {
  width: 180px;
  height: 230px;
  display: block;
}
.avatar-lobby {
  position: relative;
  display: inline-block;
  vertical-align: bottom;
}
.avatar-lobby svg {
  width: 36px;
  height: 46px;
}
.myavatar {
  background-color: rgba(255, 255, 0, 0.3);
}

#app {
  font: "Aliens Among Us", sans-serif;
}

@font-face {
  font-family: "Aliens Among Us";
  src: url("@fonts/aliensamongus.ttf");
}

@font-face {
  font-family: "Aliens Among Us Italic";
  src: url("@fonts/aliensamongus-italic.ttf");
}
</style>
