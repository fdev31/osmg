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