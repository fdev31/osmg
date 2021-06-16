// Il faut déterminer comment se lance le jeu . Cela nécessite de répérer le créateur de la session. Vérifier la présence de chacun au début et pendant le jeu
// Il faut vérifier que chacun soit synchrone avec l'état de la partie
// Le client doit connaitre sa propre identité
// Api Start lance la partie. Elle doit se lancer quand tout le monde a fait start ?

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

const dices = {
    "ONE_FACE" : "dice-six-faces-one.svg",
    "TWO_FACE" : "dice-six-faces-two.svg",
    "THREE_FACE" : "dice-six-faces-three.svg",
    "FOUR_FACE" : "dice-six-faces-four.svg",
    "FIVE_FACE" : "dice-six-faces-five.svg",
    "SIX_FACE" : "dice-six-faces-six.svg",
}

function isError(res) {
    return res && res.detail != undefined;
}

function checkLost() {
    if (marathon.remain < 0) {
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
                alert("A toi de jouer!");
            }
        }
    },
    varUpdate: (data) => {
        console.log(data);
        if (data.var == "distance") {
            console.log(data.player, marathon.myId);
            if (data.player == marathon.myId) {
                marathon.remain = data.val;
            }
        }
        checkLost();
    },
    newTurn: (data) => {
        checkLost();
        marathon.turn = data.val;
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
        alert(message);
    }
};

function initApp() {
    let host = document.location.host;
    try {
        var data = extractJsonFromCookie();
    } catch (e) {
        window.location = `http://${host}/static/index.html`;
    }

    if (typeof data.name == "undefined" || data.name == null) {
        window.location = `http://${host}/static/lobby.html`;
    }

    // if (data.status == undefined) {
        Object.assign(data,
            {
                host: document.location.host,
                status: 0,
                remain: 42195, // FIXME: this is a duplicate of player data !
                turn: 0, // FIXME: this is a duplicate of game data !
                choice: 0,
                svg : [],
                mousePosition : [0,0]
            }
        )
    // }
    marathon = new Vue({
        el: "#app",
        data: data ,
        mounted : function () {
          this.enableSnap()
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
                    console.log(diceArray);

                    this.choice = parseInt(diceArray.join(''));
                    this.setStatus(statuses.DICE_THROWN);

                } catch (e) {
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
                var choice =  Array.from(this.choice.toString()).map((o)=>parseInt(o));
                // XXX: will grey out the buttons instead
                let action = await post(`http://${host}/game/marathon/validateDice?value=${this.choice}`, {
                    "id":parseInt(this.myId),
                    "secret": parseInt(this.secret),
                    "sessionName":this.name
                });
                if (isError(action)) {
                    alert(action.detail);
                } else {
                    this.setStatus ( statuses.END_TURN );
                    this.choice = '';
                }
            },
            finalOwnData : function() {
                for (var [key , player] of this.playersData) {
                    console.log(key);
                }
            },
            enableDragDrop : function (element) {
            var move = function(dx,dy) {
                    this.attr({
                                transform: this.data('origTransform') + (this.data('origTransform') ? "T" : "t") + [dx, 0]
                            });
            }
            var start = function() {
                    this.data('origTransform', this.transform().local );
            }
            var stop = function(mouseEvent) {
                    console.log('finished dragging');
            }
            element.drag(move, start, stop );


          },
            enableSnap : function() {
              this.svg.push(Snap("#svg6684"));
              var choice = [1,2,3,4]
              for (var i = 1; i < choice.length; i++) {
                this.svg.push(this.svg[0].clone())
                // this.choice[i]
                this.enableDragDrop(this.svg[i])
              }
              this.enableDragDrop(this.svg[0])
            }
        }
    });
    setupStreamEventHandler({topic :marathon.name , uid : marathon.myId}, handlers);
    fetch('avatars.svg')
        .then( async (q) => {
            let text =  await q.text();
            for (let player of marathon.players) {
                let domid = 'avatar_'+player.id;
                document.getElementById(domid).innerHTML = text;
                avatar = new Avatar('#'+domid);
                avatar.fromName(player.name);
            }
        });
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




  function rotateElement(element, angle) {
  var bbox = s.getBBox();
  s.stop().animate({ transform: `r${angle},0,0} `}, 500, mina.easeinout);
  }

  function onSVGLoaded( data ){
    s.append( data );
}
