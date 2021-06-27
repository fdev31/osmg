let avatarCode;

handlers = {
    'newPlayer': (data) => {
        delete data['cat'];
        lobby.players.push(data);
        setCookie(Vue2Obj(lobby));
    },
};

function initApp() {
    initLocales();
    let data = extractJsonFromCookie();
    data.host = document.location.host;
    let app = Vue.createApp({
        components: {
            'player-list': window['player-list'],
        },
        watch: {
            players(val) {
                this.$refs.playerlist.players = val;
            }
        },
        data() { return data},
        mounted() {
            this.$refs.playerlist.players = this.players;
        },
        methods : {
          T(text) {
              return getTranslation(text)
          },
          startGame : async function () {
            start = await post(`http://${this.host}/c/session/start`, {
              "id": this.myId,
              "sessionName": this.name
            });
            window.location = `/static/game_${this.gameType}.html`;
          }
        }
    });
    lobby = app.mount('#app')
    setupStreamEventHandler({topic: lobby.name, uid: lobby.myId}, handlers);
}
