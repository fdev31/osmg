<script setup>
import { RouterLink, RouterView } from "vue-router";
import HelloWorld from "./components/HelloWorld.vue";
</script>

<script>
export default {
  mounted() {
    this.$router.push("/");
  },
};
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
