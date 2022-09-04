<script setup>
import {
  VueNotificationList,
  useNotificationStore,
} from "@dafcoe/vue-notification"; // component
import "@dafcoe/vue-notification/dist/vue-notification.css"; // style
import { isDarkMode } from "@/lib/utils.js";
const { setNotification } = useNotificationStore();

const prop = defineProps({
  position: {
    type: String,
    default: "top-right",
  },
});

function show(text, opts = {}) {
  const notif = {
    message: text,
    type: "info", // "info"|"warning"|"alert"|"success"
    appearance: isDarkMode() ? "dark" : "light", // "light"|"dark"|"glass"
    dismiss: { manually: true, automatically: !opts.sticky },
    showDurationProgress: true,
    showIcon: true,
    duration: 3000,
  };
  Object.assign(notif, opts);
  setNotification(notif);
}
defineExpose({ show });
</script>

<template>
  <vue-notification-list :position="prop.position" />
</template>
