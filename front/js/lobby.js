let avatarCode;
let statuses = {
    "NOT_READY" : 0,
    "READY" : 1
}


toaster = new Toaster();
function counter(index ,time=1000) {
    return new Promise((res)=> {
        setTimeout(()=>{
            toaster.show({message:index});
            res()
        }, time)
    })
}
async function countDown(count=4) {
    return new Promise(async (resolve)=>{
        for (let index = 0; index < count; index++) {
            let display =  count - (index + 1) == 0 ? "Go !" : count - (index + 1)
            await counter(display , 1500).then(console.log("ready"));
        }
        resolve();
    })

}
handlers = {
    connectPlayer:(data) => {
        toaster.show({message: `${findPlayer(lobby,data.id).name} enters the game` ,time: 2500})
        console.log(data);
    },
    disconnectPlayer:(data)=>{
        toaster.show({message : `${findPlayer(lobby,data.id).name} is disconnected` , time : 2500})
        console.log(data);
    },
    'curPlayer' : (data) =>{
        lobby.gameData.curPlayer = data.val;
        setCookie(Vue2Obj(lobby));
    },
    'newPlayer': (data) => {
        delete data['cat'];
        lobby.players.push(data);
        setCookie(Vue2Obj(lobby));
    },
    'start':async (data) => {
        countDown().then(()=> {
            window.location = `/game_${lobby.gameType}.html`;
        });
    },
    'voteStart':(data)=> {
        console.log(data);
    },
    'voteEnd':(data)=> {
        console.log(data);
    },
    'log': (data) =>{
        console.log(data);
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
          kickPlayer : async function (player) {
            let appliant;
                this.players.map((p)=> {
                    if (parseInt(p.id) === parseInt(this.myId)) appliant = p;
                })
                let description = `${appliant.name}%20veut%20d%C3%A9gager%20${player.name}`
                let url = `http://${document.location.host}/c/session/vote?name=kick_${player.id}&validate=true&description=${description}`;
                let action = await post(url, {
                    "id":parseInt(this.myId),
                    "secret": parseInt(this.secret),
                    "sessionName":this.name
                });
          },
          voteYes: function(){
              console.log("yes");
          },
          voteNo: function(){
            console.log("no");
        }

        }
    });
    lobby = app.mount('#app')
    setupStreamEventHandler({topic: lobby.name, uid: lobby.myId}, handlers);
}
