<template>
  <div>
    <div :class="['content-container', sidebar_shown_on_pc_mode?'':'side-hidden-screen']">
      <ContentView ref="contentView" :base_name="contentAlbumName" :album_friendly_name="contentFriendlyName"
                   @should-show-sidebar="(val, mode) =>  mode === 'mobile' ? sidebar_shown_on_mobile_mode = val : sidebar_shown_on_pc_mode = val"
                   :sidebar_shown_pc = "sidebar_shown_on_pc_mode"
                   @preview-photo="(a,b,c,d,e,f) => previewPhoto(a,b,c,d,e,f)"
      ></ContentView>
    </div>
    <div class="sidebar-mobile-mask" v-show="sidebar_shown_on_mobile_mode" @click="sidebar_shown_on_mobile_mode = false"></div>
    <div :class="['sidebar-container', sidebar_shown_on_pc_mode?'':'side-hidden-screen', sidebar_shown_on_mobile_mode?'sidebar-mobile-shown':'']">
      <Sidebar ref="sidebar" :people_enabled="people_enabled"
               @switch-album="(album_name, friendly_name) => { this.contentAlbumName = album_name; this.contentFriendlyName = friendly_name; }"
               @should-show-sidebar="(val, mode) =>  mode === 'mobile' ? sidebar_shown_on_mobile_mode = val : sidebar_shown_on_pc_mode = val"
               @open-settings="settings_shown = true"
      ></Sidebar>
    </div>
    <transition name="preview-slide">
      <div class="preview-container" v-if="preview_shown">
        <Preview  :current_photo_filename="preview_filename" :image_list="preview_imagelist" :index="preview_index" :current_album_name="preview_album_name"
                  :catalog_name="contentFriendlyName" :current_photo="preview_current_obj" :photo_count="preview_photo_count"
                  @hide-preview="preview_shown = false"
                  @change-photo="(a,b,c,d,e) => previewPhoto(a,b,c,d,e, preview_photo_count)"
                  @load-more-photos="(targetIndex) => loadMorePhotos(targetIndex)"
        ></Preview>
      </div>
    </transition>
    <div class="password-container" v-show="password_input_shown">
      <PasswordInput ref="password_input" @submit-password="pwd => checkPassword(pwd)"></PasswordInput>
    </div>
    <div class="settings-container" v-show="settings_shown">
      <Settings @close-settings="settings_shown = false"></Settings>
    </div>
  </div>
</template>

<script>
import Sidebar from "@/components/Sidebar";
import ContentView from "@/components/Content";
import Preview from '@/components/Preview';
import PasswordInput from "@/components/PasswordInput";
import Settings from "@/components/Settings";

import utils from "@/js/utils";
let md5 = require('js-md5');

export default {
  name: 'App',
  components: {
    Sidebar, ContentView, Preview, PasswordInput, Settings
  },
  data: () => ({
    activeName: 'beautiful-album',
    content_view_shown: true,
    sidebar_shown_on_mobile_mode: false,
    sidebar_shown_on_pc_mode: true,
    password_input_shown: false,
    settings_shown: false,

    preview_shown: false,
    preview_filename: '',
    preview_imagelist: [],
    preview_index: 0,
    preview_album_name: '',
    preview_current_obj: '',
    preview_photo_count: 0,

    contentAlbumName: "",
    contentFriendlyName: "",

    // People feature in Sidebar
    people_enabled: false,
  }),
  methods: {
    tr(x, ...args) { return utils.translate(x, ...args) },
    previewPhoto(filename, photo_list, index, album_name, photo_obj, photo_count) {
      this.preview_filename = filename;
      this.preview_index = index;
      this.preview_imagelist = photo_list;
      this.preview_album_name = album_name;
      this.preview_current_obj = photo_obj;
      this.preview_photo_count = photo_count || photo_list.length;
      this.preview_shown = true;
    },
    async loadMorePhotos(targetIndex) {
      if (this.$refs.contentView) {
        await this.$refs.contentView.load_image();
        // 等待加载完成后，检查目标索引是否已加载，如果是则切换
        this.$nextTick(() => {
          // 使用 Content 的 photo_list，它应该和 preview_imagelist 是同一个引用
          const photoList = this.$refs.contentView.photo_list;
          if (targetIndex !== undefined && photoList && targetIndex < photoList.length) {
            const photo = photoList[targetIndex];
            this.previewPhoto(photo.name, photoList, targetIndex, photo.al, photo, this.preview_photo_count);
          }
        });
      }
    },

    async requirePassword() {
      this.password_input_shown = true;
    },

    async checkPassword(pwd) {
      // check if is share link
      if (window.is_share_link) {
        let album_hash = utils.md5_transform(window.share_id, pwd);
        console.log("share id:  ", window.share_id);
        console.log("password:  ", pwd);
        console.log("album_hash:", album_hash);

        try {
          await utils.get_json(`shared/${album_hash}-get-photo-count`);
          this.$refs.password_input.feedback(true);
          this.password_input_shown = false;

          this.initialize_for_share(album_hash); // initialize for share link
        }
        catch (ee) {
          this.requirePassword();
          this.$refs.password_input.feedback(false);
        }
        return;
      }

      // is a normal login
      window.miyuki_password = pwd
      window.enabled_password = true;
      try {
        await utils.get_secured_json('get-album');
        localStorage.setItem("password", pwd)
        this.$refs.password_input.feedback(true);
        this.password_input_shown = false;
        this.initialize();
      }
      catch (ee) {
        localStorage.removeItem("password");
        this.requirePassword();
        this.$refs.password_input.feedback(false);
      }
    },

    initialize() {
      this.$refs.sidebar.getAlbumList();

      this.contentAlbumName = "/all";
      this.contentFriendlyName = this.tr("sidebar.photo_library");
    },

    initialize_for_share(album_hash) {
      this.$refs.sidebar.getAlbumListForShare(album_hash);

      this.contentAlbumName = "/share";
      this.contentFriendlyName = this.tr("sidebar.shared_album");
    },
  },
  async mounted() {
    if (window.innerWidth <= 500)
      this.sidebar_shown_on_mobile_mode = true;

    // Check if password enabled
    let password_enabled;

    function parse_args() {
      let _args = {};
      let args = location.href.split("?")[1];
      if (typeof args == "undefined")
        return _args;
      args.split('&').forEach(function(item) {
        var s = item.split('=');
        _args[s[0]] = s[1];
      });
      return _args;
    }
    let _args = parse_args();

    // check if is a share link
    window.is_share_link = typeof _args["shared_id"] !== "undefined";
    window.share_id = String(_args["shared_id"]).padEnd(32, "0")
    password_enabled = window.is_share_link;

    if (window.is_share_link) {
      // clear stored password if is a share link
      localStorage.removeItem('password');
    }

    if (!window.is_share_link) {
      const app_config = await utils.get_json('password');
      password_enabled = app_config.enabled;
      this.people_enabled = app_config.people_enabled;
    }

    let __TRUE__ = true;
    if (password_enabled) {
      if (localStorage.getItem("password") !== null) {
        this.checkPassword(localStorage.getItem("password"))
      }
      else this.requirePassword();
    }
    else {
      window.enabled_password = false;
      this.initialize();
    }

  }
}
</script>

<style>
body {
  margin: 0;
}

#app {
  font-family: Avenir, Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  color: #2c3e50;
  margin-top: 10px;
}

/* TODO: Consider mobile devices */

.sidebar-container {
  position: fixed;
  top: 0;
  left: 0;
  display: inline-block;
  width: 25%;
  height: 100%;
  background: aliceblue;
}
.content-container {
  position: fixed;
  top: 0;
  right: 0;
  display: inline-block;
  width: 75%;
  background: #fff;
  height: 100%;
}

.sidebar-container.sidebar-hidden {
  display: none;
  position: fixed;
  z-index: 2333;
  top: 0;
  width: 300px;
  height: 100%;
}
.sidebar-container.sidebar-hidden {
  display: block;
}
.content-container.sidebar-hidden {
  width: 100%;
}

.sidebar-container.side-hidden-screen {
  display: none;
}
.content-container.side-hidden-screen {
  left: 0;
  width: 100%;
}

.navbar.sidebar-hidden {
  width: 300px !important;
}

.sidebar-mobile-mask {
  position: fixed;
  background: rgba(0,0,0,0.1);
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;

  display: none;
}

@media screen and (min-width: 1400px) {
  .sidebar-container {
    width: 20%;
  }
  .content-container {
    width: 80%;
  }
}

@media screen and (max-width: 1100px) {
  .sidebar-container {
    display: none;
    position: fixed;
    z-index: 2333;
    top: 0;
    width: 300px;
    height: 100%;
  }
  .sidebar-container.sidebar-hidden {
    display: none;
  }
  .sidebar-container.sidebar-mobile-shown {
    display: block;
  }
  .content-container {
    width: 100%;
  }

  .navbar {
    width: 300px !important;
  }
  .sidebar-mobile-mask {
    display: block;
  }
}

@media screen and (max-width: 500px) {
  .sidebar-container {
    width: 100%;
  }
  .navbar {
    width: 100% !important;
  }
}


div.preview-container {
  position: fixed;
  z-index: 9999;
  top: 0;
  left: 0;
  height: 100%;
  width: 100%;
}

/* Preview 页面动画 */
.preview-slide-enter-active {
  transition: transform 0.2s;
}

.preview-slide-leave-active {
  transition: transform 0.2s;
}

.preview-slide-enter {
  transform: translateX(100%);
}

.preview-slide-leave-to {
  transform: translateX(100%);
}

div.settings-container {
  position: fixed;
  z-index: 10000;
  top: 0;
  left: 0;
  height: 100%;
  width: 100%;
}
</style>
