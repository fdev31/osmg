
function showResults(throws) {
  result = ""
  for (var i = 0; i < throws.length; i++) {
    result = result + `${throws[i]} `;
  }
  return result;
}
async function getThrowResults(throws) {


  if (!Number.isInteger(throws)) throw 'Paramater is not an integer';
  var myHeaders = new Headers();
  myHeaders.append("Content-Type", "application/json");

  var raw = JSON.stringify({"faces":6,"count":throws});

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
async function check_choice(choice) {
  return true
}
