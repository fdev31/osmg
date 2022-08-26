import { terser } from "rollup-plugin-terser";
import { visualizer } from "rollup-plugin-visualizer";
import json from "@rollup/plugin-json";
import vue from "rollup-plugin-vue";
import strip from "@rollup/plugin-strip";
//import analyze from "rollup-plugin-analyzer";
import cssbundle from "rollup-plugin-css-bundle";
import nodeResolve from "rollup-plugin-node-resolve";
import commonjs from "rollup-plugin-commonjs";

const globals = {};

//const dev_packages = process.env["DIST"]
//  ? [strip(), terser(), analyze(), visualizer()]
//  : [];

const plugins = [
  nodeResolve({ preferBuiltins: false, mainFields: ["module"] }),
  vue({ css: true, target: "browser", preprocessStyles: true }),
  json(),
  commonjs(),
  cssbundle(),
  strip(),
  terser(),
  visualizer(),
  //  ...dev_packages,
];

const COMP_PREFIX = "components/";
const COMP_OUT = "front/jscomp/";

function Comp(name) {
  return {
    input: `${COMP_PREFIX}${name}.vue`,
    plugins,
    output: {
      extend: true,
      globals,
      name: `${name}`,
      format: "iife",
      sourcemap: true,
      validate: true,
      compact: true,
      file: `${COMP_OUT}${name}.js`,
    },
  };
}

import * as fs from "fs";

const components = [];

fs.readdirSync("components").forEach((f) => {
  if (f.match(/\.vue$/)) {
    const base = f.substr(0, f.length - 4);
    const src_ts = fs.statSync(COMP_PREFIX + f).mtimeMs;
    const dst_ts = fs.statSync(COMP_OUT + base + ".js").mtimeMs;
    if (src_ts > dst_ts) {
      components.push(Comp(base));
    } else {
      console.log(`${f} is up to date, skipping...`);
    }
  }
});

if (components.length == 0) {
  console.log("Nothing to do!");
  process.exit(0);
}
export default components;
