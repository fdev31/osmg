<script setup>
const width = 64;
const prop = defineProps({
  x: { type: Number, default: 0 },
  y: { type: Number, default: 0 },
  idx: { type: Number, default: 0 },
  state: { type: String, default: "" },
});

function getClass(idx, state) {
  if (idx) return `pawn p${idx} ${state}`;
  return `pawn ${state}`;
}
const emit = defineEmits(["pawnClick"]);
</script>

<template>
  <div
    @click="$parent.$emit('pawnClick', prop)"
    :class="getClass(prop.idx, prop.state)"
    :style="`left: ${prop.x * width}px; top: ${prop.y * width}px;`"
  ></div>
</template>

<style scoped>
.pawn {
  width: 64px;
  height: 64px;
  position: absolute;
  background-color: rgb(214, 215, 196);
  border: solid 1px grey;
  cursor: pointer;
}
.pawn.clicked {
  border: solid 2px black;
}
.p1 {
  background-color: blue;
}
.p2 {
  background-color: red;
}
.p3 {
  background-color: green;
}
.p4 {
  background-color: yellow;
}
</style>
