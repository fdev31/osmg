

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
        mounted() {
            setPodiumLocation("Capa_1")
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
                    return result.push(data[key])
                });
                result.sort(function(a , b){
                    return a.distance - b.distance;
                });
                return result;
            }

        }
        
    });
    endgame = app.mount('#app');
}

function setPodiumLocation(elemId) {
    let finalistsElts = document.getElementsByClassName("finalist");
    let svgDim= document.getElementById(elemId).getBoundingClientRect();
    for (const elt of finalistsElts) {
        switch (0) {
            case 0:
                elt.style.top = svgDim.height * (1/5);elt.style.left = svgDim.width * (1/3);
                break;
            case 1:
                elt.style.top = svgDim.height/2;elt.style.left = svgDim.width * (2/3);
                break;     
            case 2:
                elt.style.top = svgDim.height/2;elt.style.left = 1;
                break;                                    
            default:
                elt.style.top = svgDim.height/2;elt.style.left = svgDim.width * (1/3);
                break;
        }
    }

}