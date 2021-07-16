let avatarCode;
let statuses = {
    "NOT_READY" : 0,
    "READY" : 1
}
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
    data.status = 0;
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
            this.status = 1;
          },
          playerNotReady : function () {
            // this.status = 0;   
          },
          mainAction : function () {
            switch (this.status) {
                case statuses.NOT_READY:
                    this.playerIsReady();
                    break;
                case statuses.READY:
                    this.playerNotReady();
                    break;            
                default:
                    this.playerNotReady();
                    break;
            }
          },
          getMainActionText : function () {
              return [this.T("Ready") , this.T("I'm not ready")][this.status]
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
