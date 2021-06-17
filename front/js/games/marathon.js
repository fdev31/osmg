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
        if (data.player) {
            marathon.playersData[data.player][data.var] = data.val;
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
        alert(message);
    }
};

function getDiceOrder() {
    let dices = Array.from(document.querySelectorAll('.diceArea svg')).map( (o, i)=> [o.getBoundingClientRect().x, i]);
    return dices.sort((a, b) => a[0]-b[0]).map( (o)=> o[1] );
}

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

    if (data.status == undefined) { // please do not remove this check, it was a huge bug...
        // if you do so for some reason, we need to discuss solutions
        // Do not remove code which has been added if you don't know what it's doing ;)
        Object.assign(data, {
                host: document.location.host,
                status: 0,
                remain: 42195, // FIXME: this is a duplicate of player data !
                choice: 0,
            })
    }
    data.svg = []; // XXX: do you need it in app data ? looks strange since it's not even done with the template
    const NB_DICE = 4;

    app = Vue.createApp({
        'data': function() { return data },
        mounted : function () {
          this.enableSnap()
        },
        computed: {
            turn() {
                return parseInt(this.gameData.turns) + 1;
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
                let prevState = {}
                var move = function(dx,dy) {
                    this.attr({
                        transform: this.data('origTransform') + (this.data('origTransform') ? "T" : "t") + [dx, 0]
                    });
                }
                var start = function() {
                    this.addClass('grabbed');
                    this.data('origTransform', this.transform().local );
                }
                var stop = function(mouseEvent) {
                    this.data('z-index', 0);
                    let newOrder = getDiceOrder();
                    console.log('finished dragging', newOrder);
                    let width = marathon.svg[0].node.getBoundingClientRect().width;
                    this.removeClass('grabbed');

                    let diffs = newOrder.map( (o, i) => (newOrder.indexOf(i)-i) *width)
                    // place dices when finished
                    for (let i=0; i<NB_DICE; i++) {
                        let sv = marathon.svg[NB_DICE-i-1]; // nodes are in reverse order
                        sv.animate({transform: `translate(${diffs[i]})`}, 300);
                    }
                }
                element.drag(move, start, stop );
          },
            enableSnap : function() {
              let ref = Snap("#diceREF");
              for (var i = 0; i < NB_DICE; i++) {
                  let elt = ref.clone();
                  elt.data('diceNR', i);
                  elt.addClass('dice');
                  elt.node.querySelector('.diceText').innerHTML = NB_DICE-i;
                  elt.node.style['width'] = '100px';
                  elt.node.style['height'] = '100px';
                  this.svg.push(elt);
                  this.enableDragDrop(elt);
              }
              ref.remove();
            }
        }
    });
    marathon = app.mount('#app');
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

    setInterval( ()=>{
        rotateElement(marathon.svg[0], 720, ~~(Math.random()*6) + 1)
    }, 2000);
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

function rotateElement(element, angle, new_val) {
    let d=100;
    let lastIndex = Math.floor(angle/90);
    for (let i=1; i<=angle/90; i++) {
        setTimeout( ()=> {
            if (i==1) element.node.querySelector('.diceText').innerHTML = '?';
            element.animate({ transform: `rotate(${i*180})`}, d, mina.easeinout);
            if (i==lastIndex) element.node.querySelector('.diceText').innerHTML = new_val;
        }, (d+10)*(i-1));
    }
}
