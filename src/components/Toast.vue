<script setup>
import {
  VueNotificationList,
  useNotificationStore,
} from "@dafcoe/vue-notification"; // component
import "@dafcoe/vue-notification/dist/vue-notification.css"; // style
const { setNotification } = useNotificationStore();

function show(text, opts = {}) {
  const notif = {
    message: text,
    type: "info",
    appearance: "dark", // ("light"|"dark"|"glass")
    dismiss: { manually: true, automatically: true },
    showDurationProgress: true,
    showIcon: true,
    duration: 5,
  };
  Object.assign(notif, opts);
  setNotification(notif);
}
defineExpose({ show });
</script>

<template>
  <vue-notification-list position="top-right" />
</template>
