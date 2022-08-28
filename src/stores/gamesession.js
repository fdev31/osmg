import { defineStore } from "pinia";

export const GameSession = defineStore({
  id: "session",
  state: () => ({
    myId: "",
    myName: "",
    gameType: "",
    name: "",
    gameData: {},
    players: [],
    playersData: [],
    secret: 0,
  }),
  actions: {
    getPlayerInfo(pid) {
      for (let player of this.players) if (player.id == pid) return player;
    },
    asObject() {
      const obj = JSON.parse(JSON.stringify(this));
      obj["$id"] = undefined;
      for (let k of Object.keys(obj)) {
        if (k[0] == "_") obj[k] = undefined;
      }
      return obj;
    },
  },
});
