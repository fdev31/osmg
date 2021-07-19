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
    gameData : Object,
    myId : Number
  },
  methods : {
    isPlaying : function(player) {
      if (this.gameData != undefined && parseInt(player.id) === parseInt(this.gameData.curPlayer)) return true
      else return false;
    },
  }
};
</script>

<style scoped lang="less"></style>

<template>
  
  <div v-for="item in players" :key="item.id" :class="{players : true , playing : isPlaying(item) ,disconnected : item.disconnected}">
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
