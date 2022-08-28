import { randomChoice } from "./utils";

const adj = [
  "Red",
  "Flying",
  "Strange",
  "Epic",
  "Funny",
  "Sad",
  "Happy",
  "Wet",
  "Black",
  "Blue",
  "Swimming",
];
const names = [
  "Squirrel",
  "Panda",
  "Banana",
  "Suit",
  "Pillow",
  "District",
  "Orange",
  "Thing",
  "Fish",
  "Dog",
  "Cat",
  "Bird",
  "Flag",
];

export function makeName() {
  return `${randomChoice(adj)} ${randomChoice(names)}`;
}
