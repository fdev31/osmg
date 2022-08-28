<script setup>
import { onMounted } from "vue";
import { RouterLink, RouterView, useRouter } from "vue-router";
import { extractJsonFromCookie } from "./lib/utils";

import { GameSession } from "@/stores/gamesession.js";
const gameSession = GameSession();
try {
  gameSession.$patch(extractJsonFromCookie());
} catch (e) {
  console.log("Bad cookie!");
}
const router = useRouter();

onMounted(async () => {
  await router.isReady();
  const sessId = router.currentRoute.value.params.session;
  if (sessId) {
    // This is a join game attempt
    gameSession.$reset();
    gameSession.$patch({ name: sessId });
  }
  if (gameSession.gameType) {
    // We already joined a game
    router.push(`/game-${gameSession.gameType}`);
  } else {
    router.push("/"); // load the home
  }
});
</script>

<template>
  <header class="wrapper">
    <nav>
      <RouterLink to="/">Home</RouterLink>
      <RouterLink to="/about">About</RouterLink>
    </nav>
  </header>

  <RouterView />
</template>

<style scoped>
nav > a {
  margin: 0 1ex;
}
</style>
