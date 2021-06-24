

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
                    return this.playersData[player.id].distance <= 0
                }).sort((a,b) => {
                    return Math.abs(this.playersData[a.id].distance) + this.playersData[b.id].distance
                })
                return result;
            },
            getLosers() {
                let result = this.players.filter( player => {
                    console.log(this.playersData[player.id].distance);
                    return this.playersData[player.id].distance > 0
                }).sort((a,b) => {
                    return this.playersData[a.id].distance - this.playersData[b.id].distance
                })
                return result;
            }

        }
        
    });
    endgame = app.mount('#app');
}
