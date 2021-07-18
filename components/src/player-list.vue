<script>
import avatarCard from "./avatar-card";

export default {
  components: { avatarCard },
  data() {
    return {
      players: [],

    };
  },
  props : {
    enableKick : Boolean,
    states : Object,
    myId : Number
  },
  methods : {
    isPlaying : function(player) {
      if (this.states.curPlayer != undefined &&parseInt(player.id) === parseInt(this.states.curPlayer)) return true;
    },
    isDisconnected: function(player) {
      if (this.states.disconnected != undefined &&this.states.disconnected.includes(player.id)) return true;
    },
  }
};
</script>

<style scoped lang="less"></style>

<template>
  
  <div v-for="item in players" :key="item.id" :class="{players : true , playing : isPlaying(item) , disconnected : isDisconnected(item)}">
    <avatar-card
      
      class="avatar-lobby"
      :avatar-name="item.name"
      :avatar-id="item.id"
    />
    <div> 
      <button v-if="enableKick && item.id != parseInt(myId)">Kick player</button>
    </div>
  </div>
</template>
