<template>
  <div class="popd">
    <div style="position: relative; height: 100%; width: 100%; margin: 0 0">
      <div class="dialog" v-show="true || password_dialog_shown">
        <div class="title">
          {{ title }}
        </div>
        <div class="ctnt" style="text-align: left">
          <slot></slot>
        </div>
        <div class="cbgroup" style="padding-top: 3px; text-align: right; padding-right: 10px">
          <button class="complete" @click="completeClick()" :disabled="!password_dialog_shown">完成</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import '../css/popup.css';
import utils from "@/js/utils";
let md5 = require('js-md5');

export default {
  name: "PasswordInput",
  props: [ "title" ],
  data: () => ({
    password_dialog_shown: true,
  }),
  methods: {
    async completeClick() {
      this.$emit('complete-click');
    },
    feedback(bResult) {
      if (!bResult) {
        this.password_dialog_shown = true;
      }
    }
  }
}
</script>

<style scoped>

</style>