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

const selfReferrences = {};

function clearAll() {
  for (const nid of Object.keys(notifications.value)) {
    unsetNotification(nid);
  }
  for (const nid of Object.keys(selfReferrences)) {
    delete selfReferrences[nid];
  }
}
function show(text, opts = {}) {
  if (opts.uniqueId && has(selfReferrences[opts.uniqueId])) return;
  const origNotifs = new Set(Object.keys(notifications.value));
  if (opts.fontSize) {
    text = `<div class="text-${opts.fontSize}">${text}</div>`;
  }
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
  const curNotifs = new Set(Object.keys(notifications.value));
  const tid = Array.from(curNotifs).filter((o) => !origNotifs.has(o))[0];
  if (opts.uniqueId) selfReferrences[opts.uniqueId] = tid;
  return tid;
}
function has(nid) {
  return !!notifications.value[nid];
}
defineExpose({ show, clearAll, has });
</script>

<template>
  <vue-notification-list :position="prop.position" />
</template>
