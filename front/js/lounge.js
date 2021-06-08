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

    setCookie(lounge) // throw TypeError : "Converting circular structure to JSON'
    }


  },
  lounge.name);
}
