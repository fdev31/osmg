import { defineStore } from "pinia";
import { setCookie, getLogger } from "../lib/utils";
import { colors } from "../lib/playercolors";

const specialProps = new Set([
  "myName",
  "save",
  "print",
  "getPlayerInfo",
  "getPlayerColor",
  "asObject",
]);
const simpleTypes = new Set([typeof 1, typeof "1", typeof true]);

const log = getLogger("gameSession");

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
    print() {
      if (log.enabled) {
        console.group("Session:");
        const plain = this.asObject();
        log.print(
          Object.keys(plain)
            .filter((k) => simpleTypes.has(typeof plain[k]))
            .map((k) => `${k}=${plain[k]}`)
            .join(" ; ")
        );
        log.table("uiStates", plain.uiStates);
        log.table("players", plain.players);
        for (const plr of Object.keys(plain.playersData)) {
          log.print(`${plr}::`);
          log.print(plain.playersData[plr]);
        }
        log.print("gameData", plain.gameData);
        console.groupEnd();
      }
    },
    save() {
      setCookie(this.asObject());
    },
    getPlayerInfo(pid) {
      for (let player of this.players) if (player.id == pid) return player;
    },
    getPlayerColor(pid) {
      for (let i in this.players)
        if (this.players[i].id == pid) return colors[i];
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
