function initApp() {
  try {
    var cookie = extractJsonFromCookie();
  } catch (e) {
    var cookie = {};
  }

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
        updateAvatar : function(text) {
          avatar.fromName(text);
      },
      validate : async function () {
        var myHeaders = new Headers();
        myHeaders.append("Content-Type", "application/json");
        var raw = JSON.stringify({"name": this.nickname,
                                  "avatar": this.avatar,
                                  "sessionName": this.session});
        var response = await fetch("/session/join", {
          method: 'POST',
          redirect: 'follow',
          headers: myHeaders,
          body: raw,
        });
        const data = await response.json();
        for (let player of data.players) {
          if (player.name == this.nickname) data.myId = player.id;
        }

        document.cookie = "JS=" + JSON.stringify(data) + '; SameSite=Strict';



        window.location = "saloon.html";
      }
    }
  })
    fetch('avatars.xml')
        .then( async (q) => {
            document.getElementById('avatar').innerHTML = await q.text();
            avatar = new Avatar('#avatar');
            avatar.fromName(lounge.nickname);
        });
}
