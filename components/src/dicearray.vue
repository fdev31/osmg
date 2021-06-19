<script>
import dice from "./dice";

export default {
  components : {dice},
  data() {
    return{
      dices: [],
    }
  }
}
</script>


<template>
  <div class="dices">
    <dice
      v-for="index in 4"
      :key="index"
    />
  </div>
</template>
