let avatarCode;

handlers = {
    'newPlayer': (data) => {
        delete data['cat'];
        console.log(data);
        lounge.players.push(data);
        setCookie(extractObj(lounge._data));
        setTimeout( () => lounge.addPlayer(data), 100);
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
            addPlayer: (player) => {
                let domid = 'avatar_'+player.id;
                console.log(domid);
                document.getElementById(domid).innerHTML = avatarCode;
                let avatar = new Avatar('#'+domid);
                avatar.fromName(player.name);
            },
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
        avatarCode =  await q.text();
        for (let player of lounge.players) {
            lounge.addPlayer(player);
        }
    });
}
