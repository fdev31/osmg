<script setup>
import {
  VueNotificationList,
  useNotificationStore,
} from "@dafcoe/vue-notification"; // component
import "@dafcoe/vue-notification/dist/vue-notification.css"; // style
import { isDarkMode } from "@/lib/utils.js";
const { setNotification, unsetNotification, notifications } =
  useNotificationStore();

const prop = defineProps({
  position: {
    type: String,
    default: "top-right",
  },
});

const colorScheme = isDarkMode() ? "dark" : "light";

function clearAll() {
  for (const nid of Object.keys(notifications)) {
    unsetNotification(nid);
  }
}
function show(text, opts = {}) {
  const notif = {
    message: text,
    type: "info", // "info"|"warning"|"alert"|"success"
    appearance: colorScheme, // "light"|"dark"|"glass"
    dismiss: { manually: true, automatically: !opts.sticky },
    showDurationProgress: true,
    showIcon: true,
    duration: 3000,
  };
  Object.assign(notif, opts);
  setNotification(notif);
}
defineExpose({ show, clearAll });
</script>

<template>
  <vue-notification-list :position="prop.position" />
</template>
