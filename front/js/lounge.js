function initApp() {
  var value = JSON.parse(document.cookie.split('; ')[0]);
  console.log(value);
  lounge = new Vue({
    el : "#app",
    data : value
  })
}
