
function initApp() {
  marathon = new Vue({
    Vue.component('marathon', {
      data: function() {
        return {
          player_action : "Lancer le dé",
          result: "Pas de dé lancé",
          remain : 42195,
          choice : 0,
        }

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
    })
  })
}
