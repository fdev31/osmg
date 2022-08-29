<script setup>
import atakksPawn from "@/components/atakksPawn.vue";
import { watch, reactive } from "vue";

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

watch(props.playersData, () => {
  board.forEach((v) => {
    v.player = getPlayerAtCoordinate(v.x, v.y);
  });
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

const previousState = {};

function setState(state, x, y, clearPrevious = true) {
  if (clearPrevious) {
    if (previousState[state] != undefined) {
      board[previousState[state]].state = "";
    }
  }
  const offset = y * props.width + x;
  previousState[state] = offset;
  board[offset].state = state;
}

defineExpose({ setState, getPlayerAtCoordinate });
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
.atakks-grid {
  background-color: rgba(50, 50, 50, 0.5);
}
</style>
