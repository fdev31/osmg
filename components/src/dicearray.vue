<script>
import dice from "./dice";

export default {
  components : {dice},
  data() {
    return{
      diceNumber: 4,
    }
  },
  methods : {
    updateDice(values) {
      for (let i=0; i < this.diceNumber ; i++) {
        let ref = `dice${i+1}`;
        this.$refs[ref].setValue(values[i] , true);
      }
    },
    getDiceValues(){
      let result = []
      for (let i=0 ; i < this.diceNumber ; i++) {
        let ref = `dice${i+1}`;
        result.push(this.$refs[ref].getValue())
      }
      return result;
    }
  }
}
</script>

<template>
  <div class="dices">
    <dice
      :ref="'dice' + index"
      v-for="index in diceNumber"
      :value="index"
      :key="index"
    />
  </div>
</template>
