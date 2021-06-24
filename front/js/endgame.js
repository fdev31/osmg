

function initApp() {
    var host = window.location.host
    try {
        var data = extractJsonFromCookie();
    }catch {
        window.location = `http://${host/static/index.html}`;
    }
    app = Vue.createApp({
        data : function () {
            return data;
        },
        components: {"avatar-card" : window["avatar-card"] , "player-list" : window["player-list"]},
        methods : {
            findPlayer(playerId) {
              return findPlayer(this , playerId);  
            },
            getSortedPlayers() {
                let data = this.playersData;
                let result = [];
                Object.keys(data).map(function(key){
                    return result.push([key , data[key]])
                });
                result = result.sort(function(a , b){
                    return a[1].distance - b[1].distance;
                }).map( x => {
                    return this.findPlayer(x[0]);
                });
                return result;
            },
            getWinners() {
                let result = this.players.filter( player => {
                    this.playersData[player.id].distance;
                })

            },
            getLosers() {

            }

        }
        
    });
    endgame = app.mount('#app');
}
