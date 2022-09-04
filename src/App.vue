<script setup>
import { onMounted } from "vue";
import { RouterLink, RouterView, useRouter } from "vue-router";
import { getLogger, extractJsonFromCookie } from "./lib/utils";

import { GameSession } from "@/stores/gamesession.js";
const log = getLogger("App");
const gameSession = GameSession();
import homeIcon from "@/assets/icons/home.svg?url";

try {
  gameSession.$patch(extractJsonFromCookie());
} catch (e) {
  log.error("Bad cookie!");
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
    if (gameSession.started) {
      router.push(`/game-${gameSession.gameType}`);
    } else {
      router.push(`/lobby`);
    }
  } else {
    router.push("/"); // load the home
  }
});
</script>

<template>
  <header class="flex">
    <nav class="h-0">
      <RouterLink to="/"
        ><img :src="homeIcon" class="hover:brightness-150 w-8 h-8 p-0 m-0" />
      </RouterLink>
    </nav>
  </header>
  <RouterView />
</template>

<style scoped></style>
