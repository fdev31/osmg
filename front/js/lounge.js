function initApp() {
   lounge = new Vue({
    el : "#app",
    data : extractJsonFromCookie()
  });
  setEventStreamHandler((data) => {
    console.log(data)
    if (data.cat == "newPlayer") {
      var newPlayer = {
          avatar : data.avatar,
          name : data.name
        }
      lounge.players.push(newPlayer);
    }

  },
  lounge.name);
}
