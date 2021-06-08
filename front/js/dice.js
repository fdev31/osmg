// Il faut déterminer comment se lance le jeu . Cela nécessite de répérer le créateur de la session. Vérifier la présence de chacun au début et pendant le jeu
// Il faut vérifier que chacun soit synchrone avec l'état de la partie
// Le client doit connaitre sa propre identité
// Api Start lance la partie. Elle doit se lancer quand tout le monde a fait start ?
function initApp() {


  try {
    var cookie = extractJsonFromCookie();
  } catch (e) {
    window.location = "http://localhost:5000/static/index.html";
  }

  if (typeof cookie.name == "undefined" || cookie.name == null) {
    window.location = "http://localhost:5000/static/saloon.html";
  }
  marathon = new Vue({
      el: "#app",
      data: {
          player_action : "Commencez le jeu",
          dice_throws : [],
          remain : 42195,
          choice : 0,
          game : cookie,
          status : "waiting"
      },
      methods: {
        throw_dices : async function () {
          this.dice_throws = await post("http://localhost:5000/game/marathon/throwDice", {
            "id":parseInt(this.game.myId),
            "sessionName":this.game.name
          });
          this.player_action =`A votre tour`;
        },
        player_advance : async function() {
          var choice = processStringToArrayNumber(this.choice.toString())
          if ( arrayEquals( choice, this.dice_throws)) {
            action = await post(`http://localhost:5000/game/marathon/validateDice?value=${this.choice}`, {
              "id":parseInt(this.game.myId),
              "sessionName":this.game.name
            });
            this.player_action =`Lancer le dé`;
          }
        },
        startGame : async function() {
          start = await post("http://localhost:5000/game/marathon/start", {
            "id":this.game.myId,
            "sessionName":this.game.name
          });
          this.player_action =`Lancer le dé`;
          return start;
        },
        finalOwnData : function() {
          for (var [key , player] of this.game.playersData) {
            console.log(key.substring(0,1))
          }
        }

      }
  });
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

  var raw = JSON.stringify({"id":this.game.myId,"sessionName":throws});

  var requestOptions = {
    method: 'POST',
    headers: myHeaders,
    body: raw,
    redirect: 'follow'
  };


  var response = await fetch("http://localhost:5000/api/getDiceResults", requestOptions);
  const result = await response.json();
  return result;


}

async function post(url , body) {
  var myHeaders = new Headers();
  myHeaders.append("Content-Type", "application/json");

  var raw = JSON.stringify(body);

  var requestOptions = {
    method: 'POST',
    headers: myHeaders,
    body: raw,
    redirect: 'follow'
  };


  var response = await fetch(url, requestOptions);
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
