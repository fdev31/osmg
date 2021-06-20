<script>
import * as Snap from "snapsvg-cjs";
import mina from "snapsvg-cjs";

export default {
   mounted() {
      this.$_snap = Snap(this.$el.querySelector('svg'));
      this.$_value = this.$attrs['value'] || '?';
      this.setValue(this.$_value);
   },
   methods: {
      getValue() {
         return this.$_value;
      },
      setValue(val, animate=false) {
         this.$_value = val;
         if (animate) {
            let d=100;
            let angle=720;
            let lastIndex = Math.floor(angle/90);
            for (let i=1; i<=angle/90; i++) {
               setTimeout( ()=> {
                     if (i==1) this.$el.querySelector('.diceText').innerHTML = '?';
                     this.$_snap.animate({ transform: `rotate(${i*180})`}, d, mina.easeinout);
                     if (i==lastIndex) this.$el.querySelector('.diceText').innerHTML = val;
               }, (d+10)*(i-1));
            }
         } else {
            this.$el.querySelector('.diceText').innerHTML = val;
         }
      }
   }
}
</script>

<style scoped lang="less"></style>

<template>
<span class="dice">
<svg
   viewBox="0 0 512 512"
   version="1.1"
   sodipodi:docname="foo.svg"
   inkscape:version="1.1 (c4e8f9ed74, 2021-05-24)"
   xmlns:inkscape="http://www.inkscape.org/namespaces/inkscape"
   xmlns:sodipodi="http://sodipodi.sourceforge.net/DTD/sodipodi-0.dtd"
   xmlns="http://www.w3.org/2000/svg"
   xmlns:svg="http://www.w3.org/2000/svg">
  <defs
     id="defs12" />
  <g
     id="g2334">
    <rect
       style="fill:#e0ddc9;fill-opacity:1;stroke:#000000;stroke-width:40;stroke-miterlimit:4;stroke-dasharray:none;stroke-opacity:1;paint-order:stroke markers fill"
       id="rect149"
       width="470.09824"
       height="470.09824"
       x="20.950882"
       y="20.950882"
       rx="145.03136"
       ry="145.03136" />
    <text
       xml:space="preserve"
       style="font-size:414.071px;line-height:1.25;font-family:sans-serif;letter-spacing:0px;word-spacing:0px;stroke-width:10.3518"
       x="120.6384"
       y="406.92969"
       id="text632"
       class="diceText"><tspan
         sodipodi:role="line"
         id="tspan630"
         x="120.6384"
         y="406.92969"
         style="stroke-width:10.3518">1</tspan></text>
  </g>
  <g
     inkscape:groupmode="layer"
     id="layer1"
     inkscape:label="Layer 1" />
</svg>
</span>
</template>
