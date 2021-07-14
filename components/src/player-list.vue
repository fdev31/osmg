<script>
import avatarCard from "./avatar-card";

export default {
  components: { avatarCard },
  data() {
    return {
      players: [],
      options : {
        kick_player : true,
      },

    };
  },
};
</script>

<style scoped lang="less"></style>

<template>
  
  <div v-for="item in players" :key="item.id" class="players">
    <avatar-card
      
      class="avatar-lobby"
      :avatar-name="item.name"
      :avatar-id="item.id"
    />
    <button v-if="options.kick_player" v-on:click="$emit('kick', item)" >Kick player</button>
  </div>
</template>
