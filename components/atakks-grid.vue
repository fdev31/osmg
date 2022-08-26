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
    <span class="atakks-row" v-for="x in createGrid()" :key="x">
      <span v-for="y in x" :class="setCellClass(y)" :key="y">X</span>
    </span>
  </div>
</template>
