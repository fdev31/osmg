let avatarCode;

handlers = {
    'newPlayer': (data) => {
        delete data['cat'];
        console.log(data);
        lobby.players.push(data);
        setCookie(extractObj(lobby._data));
        setTimeout( () => lobby.addPlayer(data), 100);
    },
    ready: (data) => {
        // data.player == id of ready player
    },
};
function initApp() {
    let data = extractJsonFromCookie();
    data.host = document.location.host;
    lobby = new Vue({
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
            start = await post(`http://${this.host}/session/start`, {
              "id":this.myId,
              "sessionName":this.name
            });
            window.location = `/static/game_${this.gameType}.html`;
          }
        }
    });
    setupStreamEventHandler({topic :lobby.name , uid : lobby.myId}, handlers);
    fetch('avatars.svg')
    .then( async (q) => {
        avatarCode =  await q.text();
        for (let player of lobby.players) {
            lobby.addPlayer(player);
        }
    });
}
