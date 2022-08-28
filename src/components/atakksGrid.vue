<script>
export default {
  props: {
    width: Number,
    height: Number,
    players: Object,
  },
  methods: {
    createGrid() {
      var grid = [];
      for (let i = 0; i < this.width; i++) {
        grid[i] = [];
        for (let j = 0; j < this.height; j++) {
          grid[i][j] = "void";
        }
      }
      this.drawPlayersPawns(grid, this.players);
      return grid;
    },

    setCellClass(code) {
      return "atakks-column " + code;
    },

    setPlayerPawnLocation(grid, pawns, id) {
      for (let coords of pawns) {
        coords = coords.split("-");
        grid[parseInt(coords[0])][parseInt(coords[1])] = "p" + id;
      }
    },

    drawPlayersPawns(grid, players) {
      var i = 1;
      for (let key in players) {
        this.setPlayerPawnLocation(grid, players[key]["pawns"], i);
        i++;
      }
    },
  },
};
</script>

<template>
  <div class="atakks-grid">
    <span v-for="x in createGrid()" :key="x" class="atakks-row">
      <span
        v-for="y in x"
        :key="y"
        class="atakks-column"
        :class="setCellClass(y)"
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
  width: 3em;
  height: 3em;
  border: solid 1px #151515;
  font-weight: bold;
  text-align: center;
  font-size: 200%;
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
