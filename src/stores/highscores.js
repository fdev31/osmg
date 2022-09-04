import { defineStore } from "pinia";

export const HighScores = defineStore({
  id: "highscores",
  state: () => ({
    ranking: [],
    winners: [],
    details: {}, // additional information for each player
  }),
});
