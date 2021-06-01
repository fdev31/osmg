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
  var myHeaders = new Headers();
  myHeaders.append("Content-Type", "application/json");

  var raw = JSON.stringify({"faces":10,"count":6});

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
