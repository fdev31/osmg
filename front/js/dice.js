
function initApp() {
  marathon = new Vue({
      el: "#app",
      data: {
          player_action : "Lancer le dé",
          result: "Pas de dé lancé",
          remain : 42195,
          choice : 0,
      },
      methods: {
        throw_dices : async function () {
          throws = await getThrowResults(4);

          this.result = showResults(throws);
          console.log(this.player_action);
          this.player_action =`Avancez de ${this.player_action} km`;
          console.log(this.player_action);
        },
        player_advance : async function() {
          if (! await check_choice(choice)) throw "Choississez les bons dés";
          this.remain -= this.choice;
          console.log(this.player_action);
          this.player_action =`Lancer le dé`;
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
async function check_choice(choice) {
  return true
}
