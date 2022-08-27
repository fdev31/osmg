<script setup>
import { onMounted } from "vue";
import { RouterLink, RouterView, useRouter } from "vue-router";
import HelloWorld from "./components/HelloWorld.vue";

import { GameSession } from "@/stores/gamesession.js";
const gameSession = GameSession();

const router = useRouter();

onMounted(async () => {
  await router.isReady();
  const sessId = router.currentRoute.value.params.session;
  if (sessId) {
    gameSession.$patch({ name: sessId });
  }
  router.push("/");
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
