<template>
  <div class="pwdi">
    <div style="position: relative; height: 100%; width: 100%; margin: 0 0">
      <div class="dialog" v-show="true || password_dialog_shown">
        <div class="title">
          {{ tr("pwdi.title") }}
        </div>
        <div class="ctnt">
          <p v-if="!passwordErrorMsgShown">{{ tr("pwdi.hint") }}</p>
          <p v-else style="color: red">{{ tr("pwdi.retry") }}</p>
          <input ref="pi" type="password" :placeholder="tr('Password')" v-model="passwordEntered" @keyup.enter="submitPassword()"/>
          <div style="padding-top: 25px; text-align: center">
            <button class="primary" style="width: 100px;" @click="submitPassword()" :disabled="!password_dialog_shown">{{ tr("OK") }}</button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import '../css/passwordinput.css';
import utils from "@/js/utils";
let md5 = require('js-md5');

export default {
  name: "PasswordInput",
  data: () => ({
    passwordErrorMsgShown: false,
    passwordEntered: '',

    password_dialog_shown: true,
    showInput: true,
  }),
  methods: {
    tr(x, ...args) { return utils.translate(x, ...args) },
    async submitPassword() {
      if (!this.password_dialog_shown) return;
      console.log('submit password: ', md5(this.passwordEntered));
      if (this.passwordEntered === '') return this.$refs.pi.focus();
      this.password_dialog_shown = false;
      this.$emit('submit-password', md5(this.passwordEntered));
    },
    feedback(bResult) {
      if (!bResult) {
        this.password_dialog_shown = true;
        this.passwordEntered = '';
        this.passwordErrorMsgShown = true;
      }
    }
  },
  watch: {
    password_dialog_shown() {

    }
  },
  mounted() {
    this.$refs.pi.focus();
  }
}
</script>

<style scoped>

</style>