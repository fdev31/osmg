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
  }
  ,methods : {
    getStatusClass : function(player , states) {
      if (states != undefined && states != null) {
        if ( parseInt(player.id) === parseInt(states.curPlayer)) return " playing";
        else if (states.disconnected != undefined &&states.disconnected.includes(player.id)) return "disconnected"        
      }
      return '';
    }
    
  }
};
</script>

<style scoped lang="less"></style>

<template>
  
  <div v-for="item in players" :key="item.id" :class="`players${getStatusClass(item,states)}`">
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
