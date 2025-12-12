<template>
  <Transition name="slide-up">
    <div v-if="visible" class="toast" :class="type">
      <span class="toast-icon">{{ icon }}</span>
      <span class="toast-message">{{ message }}</span>
    </div>
  </Transition>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  visible: { type: Boolean, default: false },
  message: { type: String, default: '' },
  type: { type: String, default: 'info' } // 'success' | 'warning' | 'error' | 'info'
})

const icon = computed(() => ({
  success: '✅',
  warning: '⚠️',
  error: '❌',
  info: 'ℹ️'
}[props.type] || 'ℹ️'))
</script>

<style scoped>
.toast {
  position: fixed;
  bottom: 100px;
  left: 50%;
  transform: translateX(-50%);
  padding: 12px 24px;
  border-radius: 12px;
  background: rgba(30, 30, 50, 0.95);
  backdrop-filter: blur(10px);
  color: white;
  font-size: 14px;
  display: flex;
  align-items: center;
  gap: 8px;
  z-index: 10000;
  box-shadow: 0 8px 32px rgba(0,0,0,0.3);
  max-width: 90%;
}

.toast.success { border-left: 4px solid #22c55e; }
.toast.warning { border-left: 4px solid #f59e0b; }
.toast.error { border-left: 4px solid #ef4444; }
.toast.info { border-left: 4px solid #3b82f6; }

.toast-icon {
  font-size: 16px;
}

.toast-message {
  flex: 1;
}

.slide-up-enter-active, .slide-up-leave-active {
  transition: all 0.3s ease;
}
.slide-up-enter-from, .slide-up-leave-to {
  transform: translateX(-50%) translateY(20px);
  opacity: 0;
}
</style>
