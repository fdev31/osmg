<script setup>
import { ref, onMounted } from "vue";
import QRCode from "qrcode";

const divRef = ref();
const props = defineProps({
  text: {
    type: String,
    default: "",
  },
});

onMounted(() => {
  console.log(QRCode);
  QRCode.toCanvas(divRef.value, props.text);
});
</script>

<template>
  <canvas ref="divRef" />
</template>
