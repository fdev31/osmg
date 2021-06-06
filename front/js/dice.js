// Il faut déterminer comment se lance le jeu . Cela nécessite de répérer le créateur de la session. Vérifier la présence de chacun au début et pendant le jeu
// Il faut vérifier que chacun soit synchrone avec l'état de la partie
// Quand dois je utiliser l'api diceAction
// Il me faut les données pour ne plus hardcoder , de quoi rafraichir l'état du jeu relancer session join
// vérifier avancé utilisateur coté serveur
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
          game : cookie
      },
      methods: {
        throw_dices : async function () {
          this.dice_throws = await getThrowResults(4);

          this.result = showResults(this.dice_throws);
          this.player_action =`Avancez de ${this.player_action} km`;
        },
        player_advance : async function() {
          console.log(arrayEquals( processStringToArrayNumber(this.choice), this.dice_throws));
          if ( arrayEquals( processStringToArrayNumber(this.choice), this.dice_throws)) {
            this.remain -= this.choice; //
            console.log(this.player_action);
            this.player_action =`Lancer le dé`;
          }




        },

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
async function getThrowResults(throws) {
  var result = []
  for (var i = 0; i < throws; i++) {
    result.push(Math.floor(Math.random() * 6))
  }
  return result

  // if (!Number.isInteger(throws)) throw 'Paramater is not an integer';
  // var myHeaders = new Headers();
  // myHeaders.append("Content-Type", "application/json");
  //
  // var raw = JSON.stringify({"faces":6,"count":throws});
  //
  // var requestOptions = {
  //   method: 'POST',
  //   headers: myHeaders,
  //   body: raw,
  //   redirect: 'follow'
  // };
  //
  //
  // var response = await fetch("http://localhost:5000/api/getDiceResults", requestOptions);
  // const result = await response.json();
  // return result;


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
