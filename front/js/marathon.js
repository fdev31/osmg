// Il faut déterminer comment se lance le jeu . Cela nécessite de répérer le créateur de la session. Vérifier la présence de chacun au début et pendant le jeu
// Il faut vérifier que chacun soit synchrone avec l'état de la partie
// Le client doit connaitre sa propre identité
// Api Start lance la partie. Elle doit se lancer quand tout le monde a fait start ?

handlers = {
    start : (data) => {
      marathon.status = 0;
    },
    curPlayer: (data) => {
        console.log(data);
        marathon.gameData.curPlayer = data.val.toString();
        if (data.val.toString() === marathon.myId.toString()) {
            marathon.status = 1;
            alert("A toi de jouer!");
        }
    },
    varUpdate: (data) => {
        console.log(data);
        if (data.var == "distance")
            console.log(data.player, marathon.myId);
            if (data.player == marathon.myId) {
                marathon.remain = data.val;
            }
    },
    newTurn: (data) => {
        marathon.turn = data.val;
    },
    endOfGame: (data) => {
        message = data.message;
        for (let player of marathon.players) {
            if (player.id == data.player) {
                message += "\nPlayer " + player.name + " wins!";
            }
        }
        alert(message);
    }
};

function initApp() {
    let host = document.location.host;
    try {
        var cookie = extractJsonFromCookie();
    } catch (e) {
        window.location = `http://${host}/static/index.html`;
    }

    if (typeof cookie.name == "undefined" || cookie.name == null) {
        window.location = `http://${host}/static/saloon.html`;
    }

    var settings = {
      player_action : ["En attente des autres joueurs","Lancez les dés" , "Avancez" , "Attendez" , "Fin du Tour", "Erreur"],
      statuses : {
        "UNINITIALIZED" : 0 ,
        "THROW" : 1 ,
        "DICE_THROWN" : 2,
        "WAITING" : 3 ,
        "END_TURN" : 4,
        "ERROR": 5
      },
      status : 0,
      dice_throws : [],
      remain : 42195,
      turn: 0,
      choice : 0,
      host: document.location.host,

    }

  var data = Object.assign({} , cookie , settings);
  marathon = new Vue({
      el: "#app",
      data: data ,
      methods: {
        throw_dices : async function () {
          try {
            this.dice_throws = await post(`http://${host}/game/marathon/throwDice`, {
              "id":parseInt(this.myId),
              "sessionName":this.name
            })

          } catch (e) {
            this.status = this.statuses.ERROR;
          }

          if (!Array.isArray(this.dice_throws)) {
              console.log(!Array.isArray(this.dice_throws));
              this.dice_throws = [];
          }
          else {
            this.choice = this.dice_throws.join('');
            this.status = this.statuses.DICE_THROWN;
          }

        },
        findPlayer : function (id) {
            for (var [key , player] of Object.entries(this.playersData)) {
                if (key.substring(1) == id) {
                  return player;
                }
            }
        },
        player_advance : async function() {
          var choice = processStringToArrayNumber(this.choice.toString())
// XXX: will grey out the buttons instead
//          if ( arrayEquals( choice, this.dice_throws)) {
            action = await post(`http://${host}/game/marathon/validateDice?value=${this.choice}`, {
              "id":parseInt(this.myId),
              "sessionName":this.name
            });
            this.status = this.statuses.END_TURN;
            this.choice = '';
//          }
        },
        finalOwnData : function() {
          for (var [key , player] of this.playersData) {
            console.log(key.substring(0,1))
          }
        }

      }
  });
    setupStreamEventHandler({topic :marathon.name , uid : marathon.myId}, handlers);
}

function updateState() {

}
function showResults(throws) {
  result = ""
  for (var i = 0; i < throws.length; i++) {
    result = result + `${throws[i]} `;
  }
  return result;
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



function processStringToArrayNumber (choice) {
  if (typeof choice !== "string") throw "argument must be a string";
  res = []
  for (var i = 0; i < choice.length; i++) {
    res.push(parseInt(choice[i]))
  }
  return res;
}
function arrayEquals(arr1 , arr2) {
  if (!Array.isArray(arr1) || !Array.isArray(arr2)) throw `arguments must be Array objects , ${typeof arr1} and ${typeof arr2} given`;
  if (arr1.length != arr2.length)return false;
  arr1.sort();
  arr2.sort();
  isEquals = true;
  arr1.every(function(element, index) {
    if (element !== arr2[index]) isEquals = false
  })
  return isEquals
}
