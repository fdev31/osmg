/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ["./index.html", "./src/**/*.{vue,js,ts}"],
  theme: {
    fontFamily: {
      title: ["Aliens Among Us"],
    },
    extend: {
      display: ["group-hover"],
    },
  },
  plugins: [],
};
