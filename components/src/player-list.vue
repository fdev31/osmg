<script>
import avatarCard from "./avatar-card";

export default {
  components: { avatarCard },
  emits: ["kick"],
  data() {
    return {
      players: [],
    };
  },
  props: {
    enableKick: Boolean,
    curPlayer: String,
    myId: Number,
  },
  methods: {
    isPlaying: function (player) {
      if (
        this.curPlayer != undefined &&
        parseInt(player.id) === parseInt(this.curPlayer)
      )
        return true;
      else return false;
    },
  },
};
</script>

<style scoped lang="less"></style>

<template>
  <transition-group name="fade">
    <div
      v-for="item in players"
      :key="item.id"
      :class="{
        players: true,
        playing: isPlaying(item),
        disconnected: item.disconnected,
      }"
    >
      <avatar-card
        class="avatar-lobby"
        :avatar-name="item.name"
        :avatar-id="item.id"
      />
      <div>
        <button
          v-on:click="$emit('kick', item, 'true')"
          v-if="enableKick && parseInt(item.id) != parseInt(myId)"
        >
          Kick player
        </button>
      </div>
    </div>
  </transition-group>
</template>
