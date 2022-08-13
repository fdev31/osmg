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
                        grid[i][j] = 0;                      
                    }           
                }
                return grid;
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
        class="atakks-column"
        v-for="y in x"
        :key="y"
        >X</span>
        </span>
    </div>
</template>