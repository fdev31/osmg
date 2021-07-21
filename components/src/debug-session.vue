<script>
export default {
    props: ["name", "data"],
    methods: {
        miscProps() {
            let blacklisted = new Set(['players', 'players_data', 'name', 'gameType', 'game_data']);
            let _p = [];
            for (let k in this.data) {
                if (!blacklisted.has(k)) _p.push(k);
            }
            return _p;
        }
    }
}
</script>

<style scoped lang="less">
</style>

<template>
<div>
    <h2>{{name}} - type {{data.gameType}}</h2>
    <ul v-for="(value, name) in data.game_data" :key="name">
        <li><b>{{name}}</b> = {{value}}</li>
    </ul>
    <div v-for="player in data.players" :key="player.id">
        <h3>Player {{player.name}} [{{player.id}}]</h3>
        <em>Secret: {{player._secret}}</em>
        <ul v-for="(value, name) in data.players_data[player.id]" :key="name">
            <li><b>{{name}}</b> = {{value}}</li>
        </ul>
        <div v-for="name in miscProps" :key="name">
            <b>{{name}}</b> = {{data[name]}}
        </div>
    </div>
</div>
</template>
