<script setup>
const props = defineProps({
  width: { type: Number, default: 7 },
  height: { type: Number, default: 7 },
  playersData: { type: Object, default: () => {} },
  dataKey: { type: String, default: "pawns" },
});

function createGrid() {
  var grid = [];
  for (let i = 0; i < props.width; i++) {
    grid[i] = [];
    for (let j = 0; j < props.height; j++) {
      grid[i][j] = "void";
    }
  }
  drawPlayersPawns(grid, props.playersData);
  return grid;
}

function setPlayerPawnLocation(grid, pawns, id) {
  for (let coords of pawns) {
    coords = coords.split("-");
    grid[parseInt(coords[0])][parseInt(coords[1])] = "p" + id;
  }
}

function drawPlayersPawns(grid, playersData) {
  var i = 1;
  for (let key in playersData) {
    setPlayerPawnLocation(grid, playersData[key][props.dataKey], i);
    i++;
  }
}
</script>

<template>
  <div class="atakks-grid">
    <span v-for="x in createGrid()" :key="x" class="atakks-row">
      <span
        v-for="y in x"
        :key="y"
        class="atakks-column"
        :class="`atakks-column ${y}`"
        >X</span
      >
    </span>
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
.atakks-grid .p1 {
  background-color: blue;
}
.atakks-grid .p2 {
  background-color: red;
}
.atakks-grid .p3 {
  background-color: green;
}
.atakks-grid .p4 {
  background-color: yellow;
}
</style>
