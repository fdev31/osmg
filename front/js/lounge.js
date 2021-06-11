handlers = {
    'newPlayer': (data)=>{
        lounge.players.push({
            avatar : data.avatar,
            name : data.name
        });
        setCookie(extractObj(lounge._data));
    },
    ready: (data) => {
        // data.player == id of ready player
    },
};
function initApp() {
    let data = extractJsonFromCookie();
    data.host = document.location.host;
    lounge = new Vue({
        el : "#app",
        data : data,
        methods : {
          startGame : async function () {
            start = await post(`http://${this.host}/game/marathon/start`, {
              "id":this.myId,
              "sessionName":this.name
            });
            window.location = `/static/${this.gameType}.html`;
          }
        }
    });
    setupStreamEventHandler({topic :lounge.name , uid : lounge.myId}, handlers);
    fetch('avatars.xml')
    .then( async (q) => {
        let text =  await q.text();
        for (let player of lounge.players) {
            let domid= 'avatar_'+player.id;
            document.getElementById(domid).innerHTML = text;
            avatar = new Avatar('#'+domid);
            avatar.fromName(player.name);
        }
    });
}
