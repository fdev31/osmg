var app = new Vue({
  el: '#dice',
  data: {
    result: 0
  },
  methods: {
    throw_dices : async function getThrowResults() {
      const result = await getDiceResult(6);
      app.result = result;
    }
  }
})


function getDiceResult(max) {
  return Math.floor(Math.random() * max)
}
