<template>
  <div class="popd" @click.self="closeSettings">
    <div class="dialog" style="max-width: 500px; max-height: 80vh; overflow-y: auto;">
      <div class="title">
        {{ tr("Settings") }}
      </div>
      <div class="ctnt" style="text-align: left">
        <div class="settings-section">
          <h3>{{ tr("General") }}</h3>
          <div class="settings-item">
            <label>{{ tr("Language") }}</label>
            <select v-model="selectedLanguage" @change="onLanguageChange">
              <option value="zh-CN">中文</option>
              <option value="en-US">English</option>
            </select>
            <p class="settings-hint">{{ tr("settings.language_hint") }}</p>
          </div>
        </div>

        <div class="settings-section">
          <h3>{{ tr("About") }}</h3>
          <div class="settings-item">
            <p>Beautiful Album</p>
            <p style="margin-top: 10px;">
              <a href="https://github.com/acane77/BeautifulAlbum" target="_blank" class="github-link">GitHub Repository</a>
            </p>
            <p style="margin-top: 10px; color: #888; font-size: 12px;">{{ tr("settings.license") }}</p>
          </div>
        </div>
      </div>
      <div class="cbgroup" style="padding-top: 3px; text-align: right; padding-right: 10px">
        <button class="complete" @click="closeSettings">{{ tr("Close") }}</button>
      </div>
    </div>
  </div>
</template>

<script>
import '../css/popup.css';
import utils from "@/js/utils";

function GetCurrentLanguage() {
    let lan = navigator.language;
    if (window.localStorage) {
        let user_set_lan = window.localStorage.getItem("language");
        if (typeof user_set_lan !== "undefined" && user_set_lan != null && user_set_lan.length) {
            lan = user_set_lan;
        }
    }
    if (lan.startsWith("en"))
        return "en-US";
    else
        return lan;
}

export default {
  name: "Settings",
  data: () => ({
    selectedLanguage: 'zh-CN',
  }),
  methods: {
    tr(x, ...args) { return utils.translate(x, ...args) },
    closeSettings() {
      this.$emit('close-settings');
    },
    onLanguageChange() {
      // 保存语言设置到 localStorage
      if (window.localStorage) {
        window.localStorage.setItem("language", this.selectedLanguage);
      }
      // 刷新页面以应用新语言
      location.reload();
    }
  },
  mounted() {
    // 使用 GetCurrentLanguage 函数获取当前语言
    this.selectedLanguage = GetCurrentLanguage();
  }
}
</script>

<style scoped>
.settings-section {
  margin-bottom: 25px;
}

.settings-section h3 {
  margin: 0 0 15px 0;
  font-size: 16px;
  color: #333;
  font-weight: bold;
}

.settings-item {
  margin-bottom: 15px;
}

.settings-item label {
  display: block;
  margin-bottom: 5px;
  color: #555;
  font-size: 14px;
}

.settings-item select {
  width: 100%;
  padding: 8px;
  border: 1px solid #ccc;
  border-radius: 5px;
  background: #fff;
  font-size: 14px;
  color: #333;
}

.settings-item p {
  margin: 5px 0;
  color: #555;
  font-size: 14px;
}

.settings-item p.settings-hint {
  margin-top: 5px;
  color: #888;
  font-size: 12px;
}

.settings-item a.github-link {
  color: #5555ff;
  text-decoration: none;
  font-size: 14px;
}

.settings-item a.github-link:hover {
  text-decoration: underline;
}

@media screen and (max-width: 500px) {
  .settings-section h3 {
    font-size: 18px;
  }
  
  .settings-item label,
  .settings-item p {
    font-size: 16px;
  }
}
</style>
