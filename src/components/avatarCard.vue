<script setup>
import { onMounted, ref } from "vue";
import { Avatar } from "@/assets/avatars.js";
import avatarTemplate from "@/assets/avatarTemplate.svg?raw";

const avatarDom = ref();
let avatarObj = null;

const props = defineProps({
  avatarId: { type: String, default: "" },
  avatarName: { type: String, default: "" },
  size: { type: String, default: "big" },
  showName: { type: Boolean, default: false },
});

function setName(n) {
  avatarObj && avatarObj.fromName(n);
}
defineExpose({ setName });

onMounted(() => {
  let _id =
    "av-" + (props.avatarId || Math.floor(Math.random() * 999999).toString(36));

  avatarDom.value.id = _id;

  avatarObj = new Avatar("#" + _id);
  // workaround to force update
  avatarDom.value.querySelector("svg").setAttribute("viewBox", `0 0 360 360`);
  if (props.avatarName) avatarObj.fromName(props.avatarName);
});
</script>

<template>
  <div ref="avatarDom" :class="`avatarCard flex flex-row avatar-${props.size}`">
    <div v-html="avatarTemplate" />
    <div
      v-if="props.showName"
      :class="`items-center text-slate-800 flex shrink avatar-${props.size} avatarName`"
    >
      {{ props.avatarName }}
    </div>
  </div>
</template>

<style scoped lang="less">
.avatarName.avatar-big {
  font-size: 400%;
}
.avatarName.avatar-small {
  font-size: 150%;
}
.avatarCard:deep(svg) {
  object-fit: cover;
}
// small
.avatar-small {
  height: 96px;
}
.avatar-small:deep(svg) {
  width: 96px;
  height: 96px;
}

@media (max-width: 1024px) {
  .avatar-big {
    height: 250px;
  }
  .avatar-big:deep(svg) {
    width: 250px;
    height: 250px;
  }
  .avatar-small {
    height: 64px;
  }
  .avatar-small:deep(svg) {
    width: 64px;
    height: 64px;
  }
}

// tiny
.avatar-tiny {
  height: 64px;
}
.avatar-tiny:deep(svg) {
  width: 64px;
  height: 64px;
}
</style>
