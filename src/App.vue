<template>
  <div id="app" class="app-wrapper">
    <router-view />
  </div>
</template>

<script setup>
import { onMounted } from 'vue'

onMounted(() => {
  console.log('📖 BookRe应用加载完成')
})
</script>

<style scoped>
.app-wrapper {
  width: 100vw;
  height: 100vh;
  overflow: hidden;
  font-family: 'Inter', 'Microsoft YaHei', 'PingFang SC', sans-serif;
}
</style>
