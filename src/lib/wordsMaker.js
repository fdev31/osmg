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
  "Shinny",
  "Funky",
  "Rocking",
  "Melting",
  "Frozen",
  "Burning",
  "Black",
  "Blue",
  "Swimming",
];
const names = [
  "Squirrel",
  "Panda",
  "Banana",
  "Suit",
  "Car",
  "Mama",
  "Dude",
  "Pal",
  "Daddy",
  "Fisherman",
  "Cook",
  "Icecube",
  "Pillow",
  "District",
  "Orange",
  "Thing",
  "Fish",
  "Dog",
  "Cat",
  "Bird",
  "Flag",
  "Potato",
  "Shoe",
  "Shirt",
  "Pants",
  "Bubble-gum",
];

export function makeName() {
  return `${randomChoice(adj)} ${randomChoice(names)}`;
}
