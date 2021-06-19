<script>
import dice from "./dice";

export default {
  components : {dice},
  data() {
    return{
      dices: [1, 2, 3, 4],
    }
  }
}
</script>

<template>
  <div class="dices">
    <dice
      v-for="index in dices"
      :value="index"
      :key="index"
    />
  </div>
</template>
