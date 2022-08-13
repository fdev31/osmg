<script>
    export default {
        props : {
            x : Number,
            y : Number
        },
        methods : {
            createGrid() {
                let grid = []
                for (let i = 0; i < this.x; i++) {
                    grid[i]=[];
                    for (let j = 0; j < this.y; j++) {
                        grid[i][j] = "void";                      
                    }           
                }
                grid[0][0]="p1"
                grid[6][6]="p2"
                return grid;
            },

            setCellClass(code) {
                return "atakks-column " + code
            }
        }
    }
</script>

<style>
.atakks-grid {
  
}

.atakks-row {
  display: inline-grid;
}

.atakks-column {
  width: 3em;
  height: 3em;
  border: solid 1px #151515;
}

.p1 {
    color:blue;
}
.p2 {
    color:red;
}
.p3 {
    color:green;
}
.p4 {
    color:yellow;
}

</style>
<template>
    <div class="atakks-grid">
        <span
        class="atakks-row"
        v-for="x in createGrid()"
        :key="x"
        >
        <span
        v-for="y in x"
        :class="setCellClass(y)"
        :key="y"
        >X</span>
        </span>
    </div>
</template>