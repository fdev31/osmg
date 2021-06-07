let lounge;

function initApp() {
  /*
  try {
    var cookie = JSON.parse(document.cookie.split('; ')[0]);
  } catch (e) { // dirty workaround for now
    window.location = "http://localhost:5000/static/index.html";
  }

  if (typeof cookie.name == "undefined" && cookie.name == null) {
    window.location = "http://localhost:5000/static/index.html";
  }
  */

  lounge = new Vue({
    el : "#app",
    data : extractJsonFromCookie()
  })
}
