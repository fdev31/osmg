
function initApp() {
  home = new Vue({
    el: "#app",
    data: {
      sessionName : "Pas de données",
      playerName : "Pas de nom",
    },
    methods: {
      play_game :  async function(game) {
        var response = await fetch("/session/new", {
          method: 'POST',
          redirect: 'follow'
        });
        const result = await response.json();
        this.sessionName = result.name;
        console.log(result);

        // create a standard player for creator of session game
        var myHeaders = new Headers();
        myHeaders.append("Content-Type", "application/json");
        var raw = JSON.stringify({"name": "Creator",
                                  "avatar": 1,
                                  "sessionName": result.name});
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
  });
}
