const statuses = {
    "UNINITIALIZED" : 0,
    "THROW" : 1 ,
    "DICE_THROWN" : 2,
    "WAITING" : 3 ,
    "END_TURN" : 4,
    "GAME_OVER": 5,
    "GAME_WON": 6,
    "ERROR": 7
}

function isError(res) {
    return res && res.detail != undefined;
}

function checkLost() {
    if (marathon.distance < 0) {
        marathon.setStatus(statuses.GAME_OVER);
        return true;
    }
}

handlers = {
    curPlayer: (data) => {
        if (!checkLost()) {
            marathon.gameData.curPlayer = data.val.toString();
            if (data.val.toString() === marathon.myId.toString()) {
                marathon.setStatus (statuses.THROW);
                toaster.show("A toi de jouer!", {time: 3500});
            }
        }
    },
    varUpdate: (data) => {
        if (data.player) {
            let pd = marathon.playersData[data.player];
            if (pd === undefined) {
                pd = marathon.playersData[data.player] = {};
            }
            pd[data.var] = data.val;
        } else {
            marathon.gameData[data.var] = data.val;
        }
        checkLost();
    },
    newTurn: (data) => {
        checkLost();
        marathon.gameData.turn = data.val;
    },
    endOfGame: (data) => {
        message = data.message;
        let myStatus = statuses.GAME_OVER;
        for (let player of marathon.players) {
            if (player.id == data.player) {
                message += "\nPlayer " + player.name + " wins!";
                if (player.id == marathon.myId) myStatus = statuses.GAME_WON;
            }
        }
        marathon.setStatus(myStatus);
        window.location = "endgame.html";
    }
};

function initApp() {
    toaster = new Toaster();
    let host = document.location.host;
    try {
        var data = extractJsonFromCookie();
    } catch (e) {
        window.location = `http://${host}/static/index.html`;
    }

    if (typeof data.name == "undefined" || data.name == null) {
        window.location = `http://${host}/static/lobby.html`;
    }

    if (data.status == undefined) { // please do not remove this check, it was a huge bug...
        // if you do so for some reason, we need to discuss solutions
        // Do not remove code which has been added if you don't know what it's doing ;)
        Object.assign(data, {
                host: document.location.host,
                status: 0,
            })
    }
    app = Vue.createApp({
        data: function() { return data },
        components: {
            'player-list': window['player-list'],
            'dice-single': window['dice'],
            'dice-array': window['dicearray'],
        },
        watch: {
            players(newVal) {
                this.$refs.playerlist.players = newVal;
            }
        },
        mounted() {
            this.$refs.playerlist.players = this.players;
        },
        computed: {
            diceVisible() {
                return [statuses.THROW, statuses.DICE_THROWN].includes(this.status);
            },
            distance() {
                return this.playersData[this.myId].distance;
            }
        },
        methods: {
            didIWin() {
                return this.status == statuses.GAME_WON;
            },
            didILose() {
                return this.status == statuses.GAME_OVER;
            },
            playerName() {
                for (let p of this.players) {
                    if (p.id == this.myId)
                        return p.name;
                }
            },
            setStatus(status) {
                this.status = status;
                setCookie(Vue2Obj(this));
            },
            getPlayerAction: function () {
                return ["En attente des autres joueurs","Lancez les dés" , "Avancez" , "Attendez" , "Fin du Tour", "Erreur"][this.status];
            },
            mainPlayButton: async function() {
                switch(this.status) {
                    case statuses.THROW:
                        await this.throw_dices();
                        break;
                    case statuses.DICE_THROWN:
                        await this.player_advance();
                        break;
                }
            },
            throw_dices: async function() {
                try {
                    let diceArray = await post(`http://${host}/game/marathon/throwDice`, {
                        "id":parseInt(this.myId),
                        "secret": parseInt(this.secret),
                        "sessionName":this.name
                    })
                    this.$refs["mydice"].diceNumber = diceArray.length;
                    this.$refs["mydice"].updateDice(diceArray);
                    this.setStatus(statuses.DICE_THROWN);

                } catch (e) {
                    toaster.show(e.message, {time: 10000});
                    this.setStatus ( statuses.ERROR );
                }
            },
            findPlayer : function (id) {
                for (var [key , player] of Object.entries(this.playersData)) {
                    if (key == id) {
                        return player;
                    }
                }
            },
            player_advance : async function () {
                let choice = this.$refs.mydice.getDiceValues().join("");

                let action = await post(`http://${host}/game/marathon/validateDice?value=${choice}`, {
                    "id":parseInt(this.myId),
                    "secret": parseInt(this.secret),
                    "sessionName":this.name
                });
                if (isError(action)) {
                    alert(action.detail);
                } else {
                    this.setStatus ( statuses.END_TURN );
                }
            },
        }
    });
    marathon = app.mount('#app');
    setupStreamEventHandler({topic :marathon.name , uid : marathon.myId}, handlers);
}

async function getThrowResults() {
    var myHeaders = new Headers();
    myHeaders.append("Content-Type", "application/json");

    var raw = JSON.stringify({"id":this.myId,"sessionName":throws});

    var requestOptions = {
        method: 'POST',
        headers: myHeaders,
        body: raw,
        redirect: 'follow'
    };

    var response = await fetch(`http://${document.location.host}/api/getDiceResults`, requestOptions);
    const result = await response.json();
    return result;
}
