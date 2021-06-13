let home;

function initApp() {
    fetch('avatars.svg')
    .then( async (q) => {
        document.getElementById('avatar').innerHTML = await q.text();
        avatar = new Avatar('#avatar');
        avatar.fromName(home.nickname);
    });
  home = new Vue({
    el: "#app",
    watch: {
        nickname: (val) => avatar.fromName(val)
    },
    data: {
      sessionName : "Pas de données",
      playerName : "Pas de nom",
      avatar : 1,
      nickname : "Ninon",
      games: {},
    },
    methods: {
      play_game :  async function(game) {
        var response = await fetch("/session/new", {
          method: 'POST',
          redirect: 'follow'
        });
        let result = await response.json();
        this.sessionName = result.name;

        // create a standard player for creator of session game
        var myHeaders = new Headers();
        myHeaders.append("Content-Type", "application/json");
        var raw = JSON.stringify({"name": this.nickname,
                                  "avatar": this.avatar,
                                  "sessionName": result.name});
        var response_player = await fetch("/session/join", {
          method: 'POST',
          redirect: 'follow',
          headers: myHeaders,
          body: raw,
        });

        result = await response_player.json();
        for (let player of result.players) {
          if (player.name == this.nickname) result.myId = player.id;
        }
        document.cookie = "JS=" + JSON.stringify(result) + '; SameSite=Strict';
        window.location = "lobby.html";
      }
    }
  });
  getJson("/gamelist").then( (data)=>{
    home.games = data;
  });
}
