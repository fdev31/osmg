<script setup>
const width = 64;
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
    :style="`left: ${prop.x * width}px; top: ${prop.y * width}px;`"
    @click="$parent.$emit('pawnClick', prop)"
  />
  <div
    :style="`left: ${prop.x * width}px; top: ${prop.y * width}px;`"
    :class="getClass(prop.idx, prop.state)"
    @click="$parent.$emit('pawnClick', prop)"
  />
</template>

<style scoped>
.pawn {
  width: 64px;
  height: 64px;
  position: absolute;
  background-color: rgb(214, 215, 196);
  border: solid 1px grey;
  cursor: pointer;
  transition-duration: 300ms;
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
