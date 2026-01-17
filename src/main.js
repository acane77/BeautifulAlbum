import Vue from 'vue'
import App from './App.vue'

Vue.config.productionTip = false

// 禁用浏览器默认缩放和手势行为
;(function() {
  // 禁用双指缩放（手势事件）
  document.addEventListener('gesturestart', function(e) {
    e.preventDefault();
  });
  document.addEventListener('gesturechange', function(e) {
    e.preventDefault();
  });
  document.addEventListener('gestureend', function(e) {
    e.preventDefault();
  });

  // 禁用鼠标滚轮缩放 (Ctrl/Cmd + 滚轮)
  document.addEventListener('wheel', function(e) {
    if (e.ctrlKey || e.metaKey) {
      e.preventDefault();
    }
  }, { passive: false });

  // 禁用键盘缩放 (Ctrl/Cmd + +/-/0)
  document.addEventListener('keydown', function(e) {
    if ((e.ctrlKey || e.metaKey) && (e.key === '+' || e.key === '-' || e.key === '=' || e.key === '0')) {
      e.preventDefault();
    }
  });

  // 禁用多指触摸缩放（但允许单指操作和双击）
  document.addEventListener('touchstart', function(e) {
    if (e.touches.length > 1) {
      e.preventDefault();
    }
  }, { passive: false });

  document.addEventListener('touchmove', function(e) {
    if (e.touches.length > 1) {
      e.preventDefault();
    }
  }, { passive: false });
}());

new Vue({
  render: h => h(App),
}).$mount('#app')
