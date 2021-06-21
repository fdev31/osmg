

function initApp() {
    var host = window.location.host
    try {
        var data = extractJsonFromCookie();
        console.log(data);
    }catch {
        window.location = `http://${host/static/index.html}`;
    }
    console.log(data);
    app = Vue.createApp({
        data : function () {
            return data;
        },
        methods : {
            findPlayer(playerId) {
              return findPlayer(this , playerId);  
            }
        }
        
    });
    endgame = app.mount('#app');
}