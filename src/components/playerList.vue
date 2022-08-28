<script>
import avatarCard from "./avatarCard.vue";

export default {
  components: { avatarCard },
  props: {
    enableKick: Boolean,
    kickText: String,
    curPlayer: String,
    myId: String,
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
        class="avatar-list"
        :showName="true"
        :small="true"
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
.players {
  border-radius: 5px;
}
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
