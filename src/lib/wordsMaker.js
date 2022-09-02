import { randomChoice } from "./utils";

const adj = [
  "Red",
  "Sexy",
  "Calm",
  "Smashed",
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
  "Hot",
  "Warm",
  "Cold",
  "Frozen",
  "Burning",
  "Black",
  "Smocky",
  "Blue",
  "Swimming",
  "Flaming",
];
const names = [
  "Squirrel",
  "Plant",
  "Sushi",
  "Ball",
  "Cube",
  "Baloon",
  "Cookie",
  "Cake",
  "Necklace",
  "Moutains",
  "Snow",
  "Rock",
  "Water",
  "Pencil",
  "Cup",
  "Fire",
  "Glasses",
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
  "String",
  "Beard",
  "Hair",
  "Lips",
];

export function makeName() {
  return `${randomChoice(adj)} ${randomChoice(names)}`;
}
