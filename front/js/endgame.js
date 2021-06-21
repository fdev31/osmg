

function initApp() {
    var host = window.location.host
    try {
        var data = extractJsonFromCookie();
        console.log(data);
    }catch {
        window.location = `http://${host/static/index.html}`;
    }
    app = Vue.createApp({
        data : function () {
            return data;
        },
        watch: {
            players(newVal) {
                this.$refs.playerlist.players = newVal;
            }
        },
        mounted() {
            this.$refs.playerlist.players = this.players;
        },
        components: {"avatar-card" : window["avatar-card"] , "player-list" : window["player-list"]},
        methods : {
            findPlayer(playerId) {
              return findPlayer(this , playerId);  
            }
        }
        
    });
    endgame = app.mount('#app');
}