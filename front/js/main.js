var app = new Vue({
  el: '#dice',
  data: {
    result: "Pas de dé lancé",
  },
  methods: {
    throw_dices : async function () {
      throws = await getThrowResults(2);
      result = ""
      for (var i = 0; i < throws.length; i++) {
        result = result + `${throws[i]} `;
      }
      this.result = result;
    }
  }
})

function getThrowResults(throws) {
  if (!Number.isInteger(throws)) throw 'Paramater is not an integer';
  console.log(throws);
  results = [];
  for (var i = 0; i < throws; i++) {
    results.push(getDiceResult(6));
  }

  return results;
}
function getDiceResult(max) {
  return Math.floor(Math.random() * max)
}
