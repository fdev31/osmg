function initApp() {

  var url = new URL(document.URL);
  var session = url.searchParams.get("session");
  lounge = new Vue({
    el : "#app",
    data : {
      session : session,
      name : "",
      avatar : "",
    } ,
    methods : {
      checkForm : async function () {
        var myHeaders = new Headers();
        myHeaders.append("Content-Type", "application/json");
        var raw = JSON.stringify({"name": this.name,
                                  "avatar": this.avatar,
                                  "sessionName": this.session});
        console.log(raw);
        var response_player = await fetch("/session/join", {
          method: 'POST',
          redirect: 'follow',
          headers: myHeaders,
          body: raw,
        });
        const player = await response_player.json();
        document.cookie = JSON.stringify(player);
        window.location = "saloon.html";
      }
    }
  })
}
