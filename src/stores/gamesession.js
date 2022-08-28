import { defineStore } from "pinia";

export const GameSession = defineStore({
  id: "session",
  state: () => ({
    myId: "",
    gameType: "",
    name: "",
    gameData: {},
    players: [],
    playersData: [],
    secret: 0,
    uiStates: {},
    started: false,
  }),
  getters: {
    myName(state) {
      return state.getPlayerInfo(state.myId).name;
    },
  },
  actions: {
    getPlayerInfo(pid) {
      for (let player of this.players) if (player.id == pid) return player;
    },
    asObject() {
      const obj = JSON.parse(JSON.stringify(this));
      for (let k of Object.keys(obj)) {
        if (k[0] == "_" || k[0] == "$") delete obj[k];
      }
      return obj;
    },
  },
});
