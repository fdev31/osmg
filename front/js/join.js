function initApp() {
  initLocales();
  var url = new URL(document.URL);
  var session = url.searchParams.get("session");
  let app = Vue.createApp({
    components: { 'avatar-card': window['avatar-card'] },
    data() { return {
      session : session,
      nickname : "Joe",
      avatar : 1,
    }} ,
    watch:{
      nickname(newVal) {
        this.$refs.myavatar.name = newVal;
      }
    } ,
    methods : {
      T(text) {
        return getTranslation(text);
      },
      validate : async function () {
        var myHeaders = new Headers();
        myHeaders.append("Content-Type", "application/json");
        var raw = JSON.stringify({"name": this.nickname,
                                  "avatar": this.avatar,
                                  "sessionName": this.session});
        var response = await fetch("/c/session/join", {
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
        window.location = "lobby.html";
      }
    }
  });
  lobby = app.mount('#app');
}
