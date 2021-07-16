let avatarCode;

handlers = {
    'newPlayer': (data) => {
        delete data['cat'];
        lobby.players.push(data);
        setCookie(Vue2Obj(lobby));
    },
    'startGame':(data) => {
        window.location = `/game_${this.gameType}.html`;
    }
};

function initApp() {
    initLocales();
    let data = extractJsonFromCookie();
    data.host = document.location.host;
    data.ready = false;
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
            document.title = this.T("lobby_title");
            this.$refs.playerlist.players = this.players;
        },
        methods : {
          T(text) {
              return getTranslation(text)
          },
          playerIsReady : async function () {
            start = await post(`http://${this.host}/c/session/start`, {
              "id": this.myId,
              "sessionName": this.name
            });
            this.ready = true;
          },
          kickPlayer : function (player) {
              console.log(player);
              alert("byebye " + player.name);
          }
        }
    });
    lobby = app.mount('#app')
    setupStreamEventHandler({topic: lobby.name, uid: lobby.myId}, handlers);
}
