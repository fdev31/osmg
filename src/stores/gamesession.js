import { defineStore } from "pinia";
import { setCookie, getLogger } from "../lib/utils";

const specialProps = new Set(["myName", "save", "getPlayerInfo", "asObject"]);

const log = getLogger("gameSession");

const simpleTypes = new Set([typeof 1, typeof "1"]);

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
      let i = state.getPlayerInfo(state.myId);
      if (i) return i.name;
    },
  },
  actions: {
    save() {
      setCookie(this.asObject());
      if (log.enabled) {
        log.table(
          "Saving...",
          Object.keys(this)
            .filter((k) => simpleTypes.has(k))
            .map((k) => this[k])
        );
        log.table("players", this.players);
        log.table("playersData", this.players);
        log.table("uiStates", this.uiStates);
      }
    },
    getPlayerInfo(pid) {
      for (let player of this.players) if (player.id == pid) return player;
    },
    asObject() {
      const obj = {};
      for (let k of Object.keys(this)) {
        if (k[0] == "_" || k[0] == "$" || specialProps.has(k)) continue;
        obj[k] = JSON.parse(JSON.stringify(this[k]));
      }
      return obj;
    },
  },
});
