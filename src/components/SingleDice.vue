<script>
import "snapsvg-cjs";
import mina from "snapsvg-cjs";

export default {
  mounted() {
    this.snap = window.Snap(this.$el.querySelector("svg"));
    this.$_value = this.$attrs["value"] || "?";
    this.setValue(this.$_value);
  },
  methods: {
    setDots(val) {
      let visibles = [];
      switch (val) {
        case 1:
          visibles = [7];
          break;
        case 2:
          visibles = [2, 5];
          break;
        case 3:
          visibles = [2, 5, 7];
          break;
        case 4:
          visibles = [1, 2, 5, 6];
          break;
        case 5:
          visibles = [1, 2, 5, 6, 7];
          break;
        case 6:
          visibles = [1, 2, 3, 4, 5, 6];
          break;
      }
      for (let i = 1; i < 8; i++) {
        let elt = this.$el.querySelector(`.dot${i}`);
        elt.style.visibility = visibles.includes(i) ? "visible" : "hidden";
      }
      this.$el.querySelector(".unknown").style.visibility = val
        ? "hidden"
        : "visible";
    },
    getValue() {
      return this.$_value;
    },
    setValue(val, animate = false) {
      this.$_value = val;
      if (animate) {
        let d = 100;
        let angle = 720;
        let lastIndex = Math.floor(angle / 90);
        this.setDots(0);
        for (let i = 1; i <= angle / 90; i++) {
          setTimeout(() => {
            this.snap.animate(
              { transform: `rotate(${i * 180})` },
              d,
              mina.easeinout
            );
            if (i == lastIndex) {
              this.setDots(val);
            }
          }, (d + 10) * (i - 1));
        }
      } else {
        this.setDots(val);
      }
    },
  },
};
</script>

<template>
  <span class="dice">
    <svg
      version="1.1"
      viewBox="0 0 512 512"
      xmlns="http://www.w3.org/2000/svg"
      xmlns:xlink="http://www.w3.org/1999/xlink"
    >
      <defs>
        <radialGradient
          id="radialGradient7948"
          cx="146.29"
          cy="140.07"
          r="58.892"
          gradientUnits="userSpaceOnUse"
        >
          <stop offset="0" />
          <stop offset="1" />
        </radialGradient>
      </defs>
      <rect
        x="20.951"
        y="20.951"
        width="470.1"
        height="470.1"
        rx="145.03"
        ry="145.03"
        fill="#ff5749"
        stroke="#000"
        stroke-width="40"
        style="paint-order: stroke markers fill"
      />
      <g transform="translate(-3.5471 -14.109)" stroke-width="7.5591">
        <circle
          class="dot1"
          cx="146.29"
          cy="140.07"
          r="58.892"
          fill="url(#radialGradient7948)"
          style="paint-order: stroke markers fill"
        />
        <g>
          <circle
            class="dot2"
            cx="372.81"
            cy="140.07"
            r="58.892"
            style="paint-order: stroke markers fill"
          />
          <circle
            class="dot3"
            cx="146.29"
            cy="270.33"
            r="58.892"
            style="paint-order: stroke markers fill"
          />
          <circle
            class="dot4"
            cx="372.81"
            cy="270.33"
            r="58.892"
            style="paint-order: stroke markers fill"
          />
          <circle
            class="dot5"
            cx="146.29"
            cy="400.15"
            r="58.892"
            style="paint-order: stroke markers fill"
          />
          <circle
            class="dot6"
            cx="372.81"
            cy="400.15"
            r="58.892"
            style="paint-order: stroke markers fill"
          />
          <circle
            class="dot7"
            cx="259.55"
            cy="270.11"
            r="58.892"
            style="paint-order: stroke markers fill"
          />
        </g>
        <path
          class="unknown"
          transform="matrix(.19484 -.72716 .72716 .19484 49.372 405.63)"
          d="m400.44 490.32-154.29-115.57-154.29 115.57 22.944-191.41-177.24-75.834 177.24-75.834-22.944-191.41 154.29 115.57 154.29-115.57-22.944 191.41 177.24 75.834-177.24 75.834z"
          fill="#ff0"
          style="paint-order: stroke markers fill"
        />
      </g>
    </svg>
  </span>
</template>

<style scoped>
.dice {
  z-index: 0;
  position: relative;
}
.dice > svg {
  width: 40px;
  height: auto;
}
</style>
