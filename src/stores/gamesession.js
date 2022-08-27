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
  },
});
