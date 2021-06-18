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
        data() { return data},
        methods : {
          startGame : async function () {
            start = await post(`http://${this.host}/session/start`, {
              "id":this.myId,
              "sessionName":this.name
            });
            window.location = `/static/game_${this.gameType}.html`;
          }
        }
    });
    fetch('avatars.svg')
    .then( async (q) => {
        avatarCode =  await q.text();
        app.component("avatar-card", getAvatarComponent(avatarCode));
        lobby = app.mount('#app')
        setupStreamEventHandler({topic :lobby.name , uid : lobby.myId}, handlers);
    });
}
