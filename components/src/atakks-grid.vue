<script>
    export default {
        props : {
            x : Number,
            y : Number,
            player : String,
            grid : Object,
        },
        methods : {
            createGrid() {

                for (let i = 0; i < this.x; i++) {
                    this.grid[i]=[];
                    for (let j = 0; j < this.y; j++) {
                        this.grid[i][j] = "void";                      
                    }           
                }
                this.grid[0][0]="p1"
                this.grid[6][6]="p2"
                return this.grid;
            },

            setCellClass(code) {
                return "atakks-column " + code
            },

            changeCell(x , y , code) {
                this.grid[x][y] = 
            }
        }
    }
</script>

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