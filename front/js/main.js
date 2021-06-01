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

async function getThrowResults(throws) {
  if (!Number.isInteger(throws)) throw 'Paramater is not an integer';
  let response = fetch('/api/getDiceResults', {faces: 6, count: throws});
  let data = await response.json();
  return data;
}
