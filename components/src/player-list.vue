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
    currentPlayer : Number,
    myId : Number
  }
  ,methods : {
    getStatusClass : function(player , id) {
      if ( parseInt(player.id) === parseInt(id)) return " playing";
      return '';
    }
    
  }
};
</script>

<style scoped lang="less"></style>

<template>
  
  <div v-for="item in players" :key="item.id" :class="`players${getStatusClass(item,currentPlayer)}`">
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
