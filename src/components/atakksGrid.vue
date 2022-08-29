<script setup>
import atakksPawn from "@/components/atakksPawn.vue";
import { reactive } from "vue";

const board = new Array(props.width * props.height).fill().map(() => {
  return reactive({});
});

const props = defineProps({
  width: { type: Number, default: 7 },
  height: { type: Number, default: 7 },
  playersData: { type: Object, default: () => {} },
  playersIds: { type: Array, default: () => [] },
  dataKey: { type: String, default: "pawns" },
});

function getPlayerAtCoordinate(x, y) {
  const str_coord = `${x}-${y}`;
  const pd = props.playersData;
  const k = props.dataKey;
  for (const pid of Object.keys(pd)) {
    if (pd[pid][k].includes(str_coord)) return pid;
  }
  return "";
}

function getPlayerNum(pid) {
  return props.playersIds.indexOf(pid) + 1;
}

board.forEach((v, i) => {
  v.x = i % props.width;
  v.y = Math.floor(i / props.width);
  v.player = getPlayerAtCoordinate(v.x, v.y);
  v.state = "";
});

let oldClicked;

function setClicked(x, y) {
  if (oldClicked != undefined) board[oldClicked].state = "";
  oldClicked = y * props.width + x;
  board[oldClicked].state = "clicked";
}

defineExpose({ setClicked });
defineEmits(["pawnClick"]); // emitted by the children component
</script>

<template>
  <div class="atakks-grid">
    <atakksPawn
      v-for="pawn in board"
      :x="pawn.x"
      :y="pawn.y"
      :state="pawn.state"
      :idx="getPlayerNum(pawn.player)"
    ></atakksPawn>
  </div>
</template>

<style scoped>
.atakks-row {
  display: inline-grid;
}
.atakks-column {
  border: solid 1px #151515;
  font-weight: bold;
  text-align: center;
  width: 2em;
  height: 2em;
}

@media (min-width: 1024px) {
  .atakks-column {
    font-size: 200%;
    width: 3em;
    height: 3em;
  }
}
.atakks-grid {
  background-color: rgba(50, 50, 50, 0.5);
}
</style>
