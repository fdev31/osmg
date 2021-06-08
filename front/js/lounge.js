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
    setEventStreamHandler((data) => {
        if(handlers[data.cat]) {
            handlers[data.cat](data)
        } else {
            console.error("No handler for "+data.cat);
            console.debug(data);
        }
    }, lounge.name);
}
