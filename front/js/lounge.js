handlers = {
    'newPlayer': (data)=>{
        lounge.players.push({
            avatar : data.avatar,
            name : data.name
        });
        setCookie(extractObj(lounge._data));
    }
};
function initApp() {
    let data = extractJsonFromCookie();
    data.host = document.location.host;
    lounge = new Vue({
        el : "#app",
        data : data
    });
    setupStreamEventHandler(lounge.name, handlers);
}
