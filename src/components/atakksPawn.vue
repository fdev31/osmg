<script setup>
const prop = defineProps({
  x: { type: Number, default: 0 },
  y: { type: Number, default: 0 },
  idx: { type: Number, default: 0 },
  state: { type: String, default: "" },
});

function getClass(idx, state) {
  if (idx) return `pawn piece p${idx} ${state}`;
  return `pawn ${state}`;
}
</script>

<template>
  <div
    :class="`pawn ${prop.state}`"
    :style="`grid-column: ${prop.x + 1}; grid-row: ${prop.y + 1}`"
    @click="$parent.$emit('pawnClick', prop)"
  />
  <div
    :style="`grid-column: ${prop.x + 1}; grid-row: ${prop.y + 1}`"
    :class="getClass(prop.idx, prop.state)"
    @click="$parent.$emit('pawnClick', prop)"
  />
</template>

<style scoped>
.pawn {
  width: 64px;
  height: 64px;
  background-color: rgb(214, 215, 196);
  border: solid 1px grey;
  cursor: pointer;
  transition-duration: 300ms;
}
@media (min-width: 1200px) {
  .pawn {
    width: 96px;
    height: 96px;
  }
}
.piece {
  z-index: 2;
  border-radius: 100px;
  scale: 0.8;
  box-shadow: black 2px 2px 5px;
}
.pawn.clicked {
  border: solid 2px black;
}
.p1 {
  background-color: #e6194b;
}
.p2 {
  background-color: #4363d8;
}
.p3 {
  background-color: #3cb44b;
}
.p4 {
  background-color: #ffe119;
}
</style>
