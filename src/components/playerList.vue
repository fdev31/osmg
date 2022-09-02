<script setup>
import avatarCard from "./avatarCard.vue";
import { colors } from "@/lib/playercolors.js";

const props = defineProps({
  enableKick: { type: Boolean, default: false },
  kickText: { type: String, default: "Kick Player" },
  curPlayer: { type: String, default: "" },
  myId: { type: String, default: "" },
  showMe: { type: Boolean, default: false },
  players: { type: Array, default: () => [] },
  size: { type: String, default: "small" },
});

defineEmits(["kick"]);

function isPlaying(player) {
  return props.curPlayer && player.id === props.curPlayer;
}
</script>

<template>
  <transition-group name="fade">
    <div class="content" v-for="(item, index) in props.players" :key="item.id">
      <div
        v-if="props.showMe || item.id != props.myId"
        :style="`border-bottom: solid 3px ${colors[index]}`"
        :class="{
          rounded: true,
          ready: item.ready,
          playing: isPlaying(item),
          disconnected: item.disconnected,
        }"
      >
        <avatarCard
          :show-name="true"
          :size="props.size"
          :avatar-name="item.name"
          :avatar-id="item.id"
        />
        <div>
          <button
            v-if="props.enableKick && item.id != props.myId"
            class="smallbtn"
            @click="$emit('kick', item, 'true')"
          >
            {{ props.kickText }}
          </button>
        </div>
      </div>
    </div>
  </transition-group>
</template>

<style scoped lang="less">
.playing {
  background-image: linear-gradient(
    rgba(255, 255, 255, 0),
    rgba(255, 255, 255, 0),
    rgb(219, 172, 63)
  );
}
.ready {
  background-color: rgba(227, 188, 33, 0.4);
}
.disconnected {
  background-color: rgba(165, 42, 42, 0.4);
}
</style>
