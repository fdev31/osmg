<script>
import avatarCard from "./avatarCard.vue";

export default {
  components: { avatarCard },
  props: {
    enableKick: Boolean,
    kickText: String,
    curPlayer: String,
    myId: Number,
  },
  emits: ["kick"],
  data() {
    return {
      players: [],
    };
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

<template>
  <transition-group name="fade">
    <div
      v-for="item in players"
      :key="item.id"
      :class="{
        players: true,
        ready: item.ready,
        playing: isPlaying(item),
        disconnected: item.disconnected,
      }"
    >
      <avatarCard
        class="avatar-lobby"
        :avatarName="item.name"
        :avatar-id="item.id"
      />
      <div>
        <button
          v-if="enableKick && parseInt(item.id) != parseInt(myId)"
          @click="$emit('kick', item, 'true')"
        >
          {{ kickText || "Kick Player" }}
        </button>
      </div>
    </div>
  </transition-group>
</template>

<style scoped lang="less">
.playing {
  background-color: rgb(138, 172, 16);
}

.ready {
  background-color: rgb(227, 188, 33);
}

.disconnected {
  background-color: brown;
}
</style>
