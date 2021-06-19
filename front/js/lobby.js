let avatarCode;

handlers = {
    'newPlayer': (data) => {
        delete data['cat'];
        lobby.players.push(data);
        setCookie(Vue2Obj(lobby));
    },
};

function initApp() {
    let data = extractJsonFromCookie();
    data.host = document.location.host;
    let app = Vue.createApp({
        components: {
            'avatar-card': window['avatar-card'],
        },
        data() { return data},
        methods : {
          startGame : async function () {
            start = await post(`http://${this.host}/session/start`, {
              "id": this.myId,
              "sessionName":this.name
            });
            window.location = `/static/game_${this.gameType}.html`;
          }
        }
    });
    lobby = app.mount('#app')
    setupStreamEventHandler({topic: lobby.name, uid: lobby.myId}, handlers);
}
