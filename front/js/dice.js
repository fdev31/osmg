// Il faut déterminer comment se lance le jeu . Cela nécessite de répérer le créateur de la session. Vérifier la présence de chacun au début et pendant le jeu
// Il faut vérifier que chacun soit synchrone avec l'état de la partie
// Le client doit connaitre sa propre identité
// Api Start lance la partie. Elle doit se lancer quand tout le monde a fait start ?
function initApp() {
  try {
    var cookie = JSON.parse(document.cookie.split('; ')[0]);
  } catch (e) {
    window.location = "http://localhost:5000/static/index.html";
  }

  if (typeof cookie.name == "undefined" && cookie.name == null) {
    window.location = "http://localhost:5000/static/saloon.html";
  }
  marathon = new Vue({
      el: "#app",
      data: {
          player_action : "Lancer le dé",
          result: "Pas de dé lancé",
          dice_throws : [],
          remain : 42195,
          choice : 0,
          game : cookie,
          status : "waiting"
      },
      methods: {
        throw_dices : async function () {
          this.dice_throws = await this.getThrowResults(4);

          this.result = showResults(this.dice_throws);
          this.player_action =`Avancez de ${this.player_action} km`;
        },
        player_advance : async function() {
          if ( arrayEquals( processStringToArrayNumber(this.choice), this.dice_throws)) {
            action = post("http://localhost:5000/game/marathon/throwDice", {
              "id":42,
              "sessionName":this.game.name
            });
            this.player_action =`Lancer le dé`;
          }
        },
        getThrowResults : async function() {
          var myHeaders = new Headers();
          myHeaders.append("Content-Type", "application/json");

          var raw = JSON.stringify({"id":42,"sessionName":this.game.name});
          var requestOptions = {
            method: 'POST',
            headers: myHeaders,
            body: raw,
            redirect: 'follow'
          };


          var response = await fetch("http://localhost:5000/game/marathon/throwDice", requestOptions);
          const result = await response.json();
          return result;
        },
        startGame : async function() {
          var myHeaders = new Headers();
          myHeaders.append("Content-Type", "application/json");

          var raw = JSON.stringify({"id":42,"sessionName":this.game.name});
          var requestOptions = {
            method: 'POST',
            headers: myHeaders,
            body: raw,
            redirect: 'follow'
          };


          var response = await fetch("http://localhost:5000/game/marathon/start", requestOptions);
          const result = await response.json();
          return result;
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

  var raw = JSON.stringify({"id":42,"sessionName":throws});

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
  if (!Array.isArray(arr1) || !Array.isArray(arr2)) throw "arguments must be Array objects";
  if (arr1.length != arr2.length)return false;
  arr1.sort();
  arr2.sort();
  isEquals = true;
  arr1.every(function(element, index) {
    if (element !== arr2[index]) isEquals = false
  })
  return isEquals
}
