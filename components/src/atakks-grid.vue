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
    <div>
        <div class="cd"
        v-for="x in createGrid()"
        :key="x"
        >
        <div
        v-for="y in x"
        :key="y"
        ></div>
        </div>
    </div>
</template>