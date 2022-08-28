<script setup>
import avatarCard from "./avatarCard.vue";

const props = defineProps({
  enableKick: { type: Boolean, default: false },
  kickText: { type: String, default: "Kick Player" },
  curPlayer: { type: String, default: "" },
  myId: { type: String, default: "" },
  players: { type: Array, default: () => [] },
});

defineEmits(["kick"]);

function isPlaying(player) {
  return props.curPlayer && player.id === props.curPlayer;
}
</script>

<template>
  <transition-group name="fade">
    <div
      v-for="item in props.players"
      :key="item.id"
      :class="{
        players: true,
        ready: item.ready,
        playing: isPlaying(item),
        disconnected: item.disconnected,
      }"
    >
      <avatarCard
        class="avatar-list"
        :show-name="true"
        :small="true"
        :avatar-name="item.name"
        :avatar-id="item.id"
      />
      <div>
        <button
          v-if="props.enableKick && item.id != props.myId"
          @click="$emit('kick', item, 'true')"
        >
          {{ props.kickText }}
        </button>
      </div>
    </div>
  </transition-group>
</template>

<style scoped lang="less">
.playing {
  background-color: rgba(138, 172, 16, 0.4);
}
.ready {
  background-color: rgba(227, 188, 33, 0.4);
}
.disconnected {
  background-color: rgba(165, 42, 42, 0.4);
}
</style>
