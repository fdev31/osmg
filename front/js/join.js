function initApp() {
  try {
    var cookie = extractJsonFromCookie();
  } catch (e) {
    var cookie = {};
  }

  // if (typeof cookie.name != "undefined" && cookie.name != null) {
  //   window.location = "http://localhost:5000/static/saloon.html";
  // }
  var url = new URL(document.URL);
  var session = url.searchParams.get("session");
  lounge = new Vue({
    el : "#app",
    data : {
      session : session,
      nickname : "San Goku",
      avatar : 1,
    } ,
    methods : {
      validate : async function () {
        var myHeaders = new Headers();
        myHeaders.append("Content-Type", "application/json");
        var raw = JSON.stringify({"name": this.nickname,
                                  "avatar": this.avatar,
                                  "sessionName": this.session});
        var response_player = await fetch("/session/join", {
          method: 'POST',
          redirect: 'follow',
          headers: myHeaders,
          body: raw,
        });
        const player = await response_player.json();
        document.cookie = "JS=" + JSON.stringify(player) + '; SameSite=Strict';
        window.location = "saloon.html";
      }
    }
  })
}
