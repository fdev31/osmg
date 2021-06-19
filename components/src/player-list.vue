<script>
import avatarCard from "./avatar-card";

export default {
  components: { avatarCard },
  data() {
    return {
    players : []
    };
  },
};
</script>

<style scoped lang="less"></style>

<template>
  <div class="players">
    <avatar-card
      v-for="item in players"
      :key="item.id"
      class="avatar-lobby"
      :avatar-name="item.name"
      :avatar-id="item.id"
    />
  </div>
</template>
