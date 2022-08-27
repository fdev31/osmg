<script setup>
import { onMounted, ref, watch } from "vue";
import avatarCard from "@/components/avatarCard.vue";
import { RouterLink } from "vue-router";

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
  games.value = await getJson("/c/gamelist");
});

async function play_game(game) {
  var response = await fetch(`/c/session/new?gameType=${game}`, {
    method: "GET",
    redirect: "follow",
  });
  let result = await response.json();
  this.sessionName = result.name;

  // create a standard player for creator of session game
  var myHeaders = new Headers();
  myHeaders.append("Content-Type", "application/json");
  var raw = JSON.stringify({
    name: this.mynickname,
    avatar: this.avatar,
    sessionName: result.name,
  });
  var response_player = await fetch("/c/session/join", {
    method: "POST",
    redirect: "follow",
    headers: myHeaders,
    body: raw,
  });

  result = await response_player.json();
  for (let player of result.players) {
    if (player.name == this.mynickname) result.myId = player.id;
  }
  setCookie(result);
  window.location = "lobby.html";
}
</script>

<template>
  <main>
    <div class="bg" v-cloak>
      <h1 class="title">{{ T("Your info") }}:</h1>
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
            :avatarName="mynickname"
            style="margin: -36px 0 0 220px"
            class="avatar"
          ></avatar-card>
        </div>
      </div>
      <h1>{{ T("Pick a game") }}:</h1>
      <div class="wrap">
        <div v-for="(info, game) in games" class="gamebutton">
          <RouterLink :to="game">
            <div class="tile">
              <!----              <span @click="play_game(game)"></span> -->
              <img :src="`./img/${info.card}.jpg`" />
              <div class="text">
                <h1>{{ T(game) }}</h1>
                <h2 class="animate-text">{{ T(game + "_description") }}</h2>
                <p
                  class="animate-text"
                  v-html="T(game + '_long_description')"
                ></p>
              </div>
              <!--             </span> -->
            </div>
          </RouterLink>
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
</style>
