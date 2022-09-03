<script>
import SingleDice from "@/components/SingleDice.vue";

function enableDragDrop(app, element) {
  var move = function (dx) {
    this.attr({
      transform:
        this.data("origTransform") +
        (this.data("origTransform") ? "T" : "t") +
        [dx, 0],
    });
  };
  var start = function () {
    this.addClass("grabbed");
    this.data("origTransform", this.transform().local);
  };
  var stop = function () {
    this.data("z-index", 0);
    let newOrder = app.getDiceOrder();
    let dices = getDices(app);
    app.updateDice(
      newOrder.map((i) => dices[i].getValue()),
      false
    );
    dices.forEach((o) => o.snap.attr({ transform: `translate(0)` }, 30));
    this.removeClass("grabbed");
  };
  element.drag(move, start, stop);
}

function getDices(app) {
  let result = [];
  for (let i = 0; i < app.diceNumber; i++) {
    let ref = `dice${i + 1}`;
    result.push(app.$refs[ref][0]);
  }
  document.debug.dices = result;
  return result;
}

export default {
  components: { SingleDice },
  data() {
    return {
      diceNumber: 4,
    };
  },
  methods: {
    enableDrag(val) {
      if (val) {
        getDices(this).forEach((o) => enableDragDrop(this, o.snap));
      } else {
        getDices(this).forEach((o) => o.snap.undrag());
      }
    },
    getDiceOrder() {
      let dices = Array.from(this.$el.querySelectorAll("svg")).map((o, i) => [
        o.getBoundingClientRect().x,
        i,
      ]);
      return dices.sort((a, b) => a[0] - b[0]).map((o) => o[1]);
    },
    updateDice(values, animate = true) {
      getDices(this).forEach((o, i) => o.setValue(values[i], animate));
    },
    getDiceValues() {
      return getDices(this).map((o) => o.getValue());
    },
  },
};
</script>

<template>
  <div class="flex flex-row">
    <SingleDice
      v-for="index in diceNumber"
      :ref="'dice' + index"
      :key="index"
      value="?"
    />
  </div>
</template>

<style scoped>
.grabbed {
  z-index: 10;
  opacity: 0.5;
}
</style>
