import { fileURLToPath, URL } from "node:url";

import { defineConfig } from "vite";
import vue from "@vitejs/plugin-vue";
import svgLoader from "vite-svg-loader";

const prodPlugins = process.env.NODE_ENV == "production" ? [] : [];
const devPlugins = process.env.NODE_ENV != "production" ? [] : [];

// https://vitejs.dev/config/
export default defineConfig({
  build: {
    sourcemap: process.env.NODE_ENV != "production",
    minify: process.env.NODE_ENV == "production",
    target: "esnext",
    outDir: "front",
  },
  plugins: [vue(), svgLoader(), ...prodPlugins, ...devPlugins],
  resolve: {
    alias: {
      "@": fileURLToPath(new URL("./src", import.meta.url)),
    },
  },
});
