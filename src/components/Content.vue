<template>
  <div  style="height: 100%; overflow-y: auto" @scroll="handleScroll">
    <div class="cnav">
      <div :class="['title', 'left', sidebar_shown_pc?'':'sidebar-hidden']">
        <span class="title-text">{{ album_friendly_name }}</span>
      </div>
      <div class="title right">
        <span style="color: #eee; margin-right: 10px;">{{ tr("content.photo_count", photo_count) }}</span>
        <button @click="menu_more_is_shown = !menu_more_is_shown" style="">...</button>
        <!-- 弹出的菜单 -->
        <div class="context-menu-mask" v-show="menu_more_is_shown" @click="menu_more_is_shown = false"></div>
        <div :class="['context-menu', menu_more_is_shown?'shown':'hidden']" v-show="menu_more_is_shown" style="top: 56px; right: 20px">
          <a href="javascript:void(0)"
             @click="current_zoom_scale < 2 && ((current_zoom_scale++), (menu_more_is_shown = false))"
             :aria-disabled="current_zoom_scale >= 2">{{ tr("content.ctx_menu.zoom_in") }}</a>
          <a href="javascript:void(0)"
             @click="current_zoom_scale > -6 && ((current_zoom_scale--), (menu_more_is_shown = false))"
             :aria-disabled="current_zoom_scale <= -6">{{ tr("content.ctx_menu.zoom_out") }}</a>
          <a href="javascript:void(0)"
             @click="current_zoom_scale != 0 && ((current_zoom_scale = 0), (menu_more_is_shown = false))"
             :aria-disabled="current_zoom_scale == 0">{{ tr("content.ctx_menu.default_scale", current_zoom_scale) }}</a>
          <hr v-show="base_name[0] !== '/'" />
          <a href="javascript:void(0)" v-show="base_name[0] !== '/'"
             @click="shareAlbumClick()"
             :aria-disabled="!share_enabled">{{ tr("content.ctx_menu.share") }}</a>
          <hr v-show="base_name === '/fav'" />
          <a href="javascript:void(0)" v-show="base_name === '/fav'"
            @click="exportFavClick()">{{ tr("content.ctx_menu.export_fav") }}</a>
          <a href="javascript:void(0)" v-show="base_name === '/fav'"
            @click="importFavClick()">{{ tr("content.ctx_menu.import_fav") }}</a>
        </div>

      </div>
      <div class="back left"   style="line-height:45px; left: 18px; top: 0" @click="raise_event_show_sidebar(true, 'mobile')">
        <i class="larrow" style="border-color: white"></i><span class="backtext">{{ tr("Photos") }}</span>
      </div>

      <div :class="['back', 'left', 'sidebar-hidden-left', sidebar_shown_pc?'':'sidebar-hidden']"
           @click="raise_event_show_sidebar(true, 'pc')" style="line-height:45px; left: 18px; top: 0">
        <span class="backtext">
          <IconBase icon-color="white"> <IconSideBar /> </IconBase>
        </span>
      </div>
    </div>

    <div>
      <div :class="['photo', 'box', 'scale-ratio-ratio-' + current_zoom_scale]" v-for="(photo, i) in photo_list" :photo-name="photo.name" :key="i"
           :style="{
                backgroundImage: `url('${ get_thumbnail_image(photo.al, photo.name) }')`,
                backgroundPosition: get_thumbnail_image_backgrouod_pos(photo)
              }"
      >
        <div class="photo-mask" style="position: absolute; left: 0; top: 0; width: 100%; height: 100%;"
             @click="raise_event_show_preview(photo.name, photo_list, i, photo.al, photo)"
        >
        </div>
        <div class="fav-btn" :style="{
                position: 'absolute', left: '20px', bottom: '20px',
                display: photo.fav ? 'block' : ''
              }"
             @click="switchFavState(photo)" >
          <IconBase icon-color="white" v-if="!photo.fav"> <IconHeart /> </IconBase>
          <IconBase icon-color="white" v-else> <IconHeartFilled /> </IconBase>
        </div>
      </div>
    </div>

    <div class="dialog-container" v-show="popup_dialog_shown">
      <PopupDialog ref="popup_dialog"
                   :title="tr('content.share_dialog.title')"
                   @complete-click="() => { popup_dialog_shown = false; }"
      >
        <div v-show="share_dialog_phase === 1 && share_enabled">
          <!-- (1) Set password for sharing -->
          <p>
            {{ tr("content.share_dialog.sharing") }}
            <span style="font-weight: bold">{{ album_friendly_name }}</span>
          </p>
          <p>{{ tr("content.share_dialog.set_password_label") }}</p>
          <p>
            <input type="password"
                   v-model="share_password"
                   style="width: calc(100% - 15px)"
                   ref="password_input" >
          </p>
          <span class="mbutton-group" style="text-align: center; display: block">
            <button class="primary large_button primary_btn"
                    @click="shareButtonClick()" >{{ tr("content.share_dialog.share_btn") }}</button>
          </span>
        </div>
        <div v-show="share_dialog_phase === 2 && share_enabled">
          <!-- (2) Show results of sharing -->
          <p>{{ tr("content.share_dialog.share_link_is") }}</p>
          <pre class="share_url">{{ share_url }}</pre>
          <p>{{ tr("content.share_dialog.share_link_desc_1") }}</p>
          <p>{{ tr("content.share_dialog.share_link_desc_2") }}</p>
        </div>
        <div v-show="!share_enabled">
          <p>{{ tr("content.share_dialog.unsharable") }}</p>
        </div>
      </PopupDialog>
    </div>
  </div>
</template>

<script>
//import IDMapping from "@/js/IDMapping";
import '../css/style.css'
import '../css/contentview.css'
import '../css/content_scale.css'
import '../css/menu.css'
import '../css/dark_theme.css'
import utils from "@/js/utils";
import IconBase from "@/icons/IconBase";
import IconSideBar from "@/icons/IconSideBar";
import IconHeart from "@/icons/IconHeart";
import IconHeartFilled from "@/icons/IconHeartFilled";
import PopupDialog from "@/components/PopupDialog";
let md5 = require('js-md5');

const PHOTO_PER_PAGE = 50;

export default {
  name: "Content",
  components: { IconSideBar, IconBase, IconHeart, IconHeartFilled, PopupDialog },
  props: [ 'base_name', 'album_friendly_name', 'sidebar_shown_pc' ],
  data() {
    return {
      page_count: 0,
      current_page_to_load: 0,
      photo_count: 0,
      photo_list: [],
      album_hash: '',
      initial_scroll_height: 0,
      response_load_new: true,
      fav_content_cache: {},
      fav_page_cache: null,
      // UI Element -- Menu
      menu_more_is_shown: false,
      current_zoom_scale: 0,
      share_enabled: false,
      // Share dialog
      popup_dialog_shown: false,
      share_dialog_phase: 1,
      share_password: "",
      share_url: "",
    }
  },
  computed: {
    album_common_prefix() {
      if (this.base_name === '/all')
        return 'get-photo-';
      if (this.base_name === '/recent')
        return 'get-recent-photo-';
      if (this.base_name === '/fav')
        return 'get-fav-photo-'; // load from localstorage
      if (this.base_name === "/share")
        return 'get-shared-photo-'; // load from another URL
      return this.base_name + '-get-photo-';
    },
    album_get_count_json_name() {
      return this.album_common_prefix + "count";
    },
    album_get_image_at_current_page_json_name() {
      return this.album_common_prefix + "page-" + String(this.current_page_to_load);
    }
  },
  watch: {
    base_name() {
      this.initialize();
    },
  },
  created() {},
  async mounted() {
    this.initialize();
  },
  methods: {
    tr(x, ...args) { return utils.translate(x, ...args) },
    raise_event_show_sidebar(val, mode) {
      this.$emit('should-show-sidebar', val, mode);
    },
    raise_event_show_preview(image_file_name, photo_list, photo_index, album_name, photo_obj) {
      this.$emit('preview-photo', image_file_name, photo_list, photo_index, album_name, photo_obj, this.photo_count);
    },
    async load_image() {
      // console.log("load album:", this.album_get_count_json_name)
      if (!this.response_load_new) {
        return;
      }
      this.response_load_new = false;
      setTimeout(() => { this.response_load_new = true; }, 1000)
      if (this.current_page_to_load >= this.page_count) {
        this.response_load_new = true;
        return;
      }
      if (this.album_get_count_json_name.startsWith("get-fav-photo-")) {
        let max_i = Math.min(this.photo_list.length + PHOTO_PER_PAGE, this.fav_page_cache.length);
        for (let i=this.photo_list.length; i < max_i; i++) {
          this.photo_list.push(this.fav_page_cache[i]);
        }
      }
      else if (this.album_get_count_json_name.startsWith("get-shared-photo-")) {
        let share_album_hash = window.share_album_hash;
        if (typeof window.share_album_hash === 'undefined') {
          throw Error('share_album_hash not defined');
        }
        console.log("share_album_hash", share_album_hash);

        this.photo_list.push(
            ...await utils.get_json(`shared/${share_album_hash}-get-photo-page-${String(this.current_page_to_load)}`));
        // Note: disable favorite feature in the sharing mode
      }
      else {
        this.photo_list.push(...await utils.get_secured_json(this.album_get_image_at_current_page_json_name));
        this.applyFavoriteWithPhotos(); // TODO: 性能优化：先执行着一条语句再加入photolist
      }

      this.current_page_to_load++;
      this.response_load_new = true;
    },
    get_thumbnail_image(alumn_name ,image_name) {
      return "/api/album-cache/" + alumn_name + "/" + image_name;
    },
    get_thumbnail_image_backgrouod_pos(photo) {
      return utils.calc_center_face_bg_pos(photo);
    },

    async initialize() {
      if (this.base_name === "")
        return;

      this.current_page_to_load = 0;
      this.photo_list = [];
      this.response_load_new = true;
      this.initial_scroll_height = 0;
      this.photo_count = this.page_count = 0;
      // this.share_enabled = false; // do not update state
      this.album_hash = '';

      // get page count
      // console.log("get photo count: ", this.album_get_count_json_name);
      if (this.album_get_count_json_name.startsWith("get-fav-photo-")) {
        // not loaded
        if (this.fav_page_cache == null || this.current_page_to_load == 0) {
          this.fav_page_cache = [];
          this.loadAllFavoriteItems();
          // console.log(this.fav_content_cache)
          for (let key1 in this.fav_content_cache) {
            // console.log(key1)
            for (let key2 in this.fav_content_cache[key1]) {
              this.fav_page_cache.push(this.fav_content_cache[key1][key2]);
            }
          }
        }
        this.photo_count = this.fav_page_cache.length;
        this.share_enabled = false; // disable share for favorite
        this.album_hash = '';

        // console.log("-- Favorite album count:", this.photo_count);
      }
      // get shared photo count
      else if (this.album_get_count_json_name.startsWith("get-shared-photo-")) {
        let share_album_hash = window.share_album_hash;
        if (typeof window.share_album_hash === 'undefined') {
          throw Error('share_album_hash not defined');
        }
        console.log("share_album_hash", share_album_hash);
        let album_config = await utils.get_json(`shared/${share_album_hash}-get-photo-count`);
        this.photo_count = album_config.count;
        this.album_hash = ''; // do not allow share for shared album
        this.share_enabled = false; // do not allow share for shared album
      }
      // get normal album
      else {
        let album_config = (await utils.get_secured_json(this.album_get_count_json_name));
        this.photo_count = album_config.count;
        this.album_hash = album_config.hash;
        this.share_enabled = typeof album_config.hash !== "undefined"
      }
      //this.photo_count = this.get_page_count(this.album_get_count_json_name);
      this.page_count = Math.ceil(this.photo_count / PHOTO_PER_PAGE);

      // load page 0 first
      if (this.page_count > 0) {
        this.load_image();
      }
    },
    handleScroll: function(el) {
      if (this.initial_scroll_height === 0)
        this.initial_scroll_height = el.srcElement.scrollHeight / 10;
      if((el.srcElement.offsetHeight + el.srcElement.scrollTop) >= el.srcElement.scrollHeight - this.initial_scroll_height) {
        this.load_image()
      }
    },

    // Favorite
    isFavorite(photo) {
      return photo.fav
    },
    /// 用于获取收藏夹对应的key
    getFavoriteStorageKey(photo) {
      return `${photo.al}/${photo.name}`;
    },
    /// 用于获取Local Storage对应的key
    getFavoriteLocalStorageKey(photo) {
      return `album_fav_${photo.al}`;
    },
    /// 用于获取local Storage中所有的key
    getFavoriteLocalStorageAllKeys() {
      let keys = []
      for (let i = 0, len = localStorage.length; i < len ; ++i) {
        let _key = localStorage.key(i);
        if (_key.startsWith("album_fav_"))
          keys.push(_key);
      }
      return keys;
    },
    loadAllFavoriteItems() {
      this.fav_content_cache = {};
      let keys = this.getFavoriteLocalStorageAllKeys();
      // console.log(keys)
      for (let i = 0; i < keys.length; i++) {
        this.fav_content_cache[keys[i]] = JSON.parse(localStorage.getItem(keys[i]));
      }
    },
    applyFavoriteWithPhotos() {
      this.loadAllFavoriteItems();
      for (let i=0; i<this.photo_list.length; i++) {
        let key = this.getFavoriteStorageKey(this.photo_list[i]);
        let al_key = this.getFavoriteLocalStorageKey(this.photo_list[i]);
        if (typeof this.fav_content_cache[al_key] == "undefined")
          continue;
        if (typeof this.fav_content_cache[al_key][key] == "undefined")
          continue;
        this.photo_list[i].fav = true;
        // console.log('-- Favorite item:', key);
      }
      this.$forceUpdate();
    },
    saveFavoriteState(photo) {
      let key = this.getFavoriteStorageKey(photo);
      let al_key = this.getFavoriteLocalStorageKey(photo);
      if (typeof this.fav_content_cache[al_key] == "undefined") {
        this.fav_content_cache[al_key] = {}
      }
      if (photo.fav) {
        // Add to favorite
        this.fav_content_cache[al_key][key] = photo;
      }
      else {
        // Remove from favorite
        delete this.fav_content_cache[al_key][key];
      }
      let localstorage = window.localStorage;
      if (typeof localstorage === "undefined") {
        alert(this.tr("content.fav.unsupported"));
        return;
      }
      // Save as <key, value> to local storage
      localstorage.setItem(
          al_key,
          JSON.stringify(this.fav_content_cache[al_key]));
    },
    switchFavState(photo) {
      photo.fav = !photo.fav;
      this.$forceUpdate();
      this.saveFavoriteState(photo)
    },

    // Share album feature
    shareAlbumClick() {
      if (typeof this.album_hash === "undefined" || this.album_hash === "") {
        return;
      }
      this.share_dialog_phase = 1;
      this.popup_dialog_shown = true;
      //this.$refs.password_input.focus();
      this.menu_more_is_shown = false;
    },
    shareButtonClick() {
      if (this.share_password === "") {
        return;
      }
      let password_hash = md5(this.share_password);
      console.log("password hash:", password_hash);
      console.log("album hash:   ", this.album_hash);
      let en = utils.md5_transform(this.album_hash, password_hash);
      let de = utils.md5_transform(en, password_hash);
      console.log("encrypted:    ", en);
      console.log("decrypted:    ", de);
      this.share_dialog_phase = 2;
      this.share_url = location.href.split("?")[0].split("#")[0] + "?shared_id=" + en;
      this.share_password = "";
    },
    exportFavClick() {
      this.menu_more_is_shown = false;
      let keys = this.getFavoriteLocalStorageAllKeys();
      console.log("export fav:", keys);
      let save_content = {};
      for (let i = 0; i < keys.length; i++) {
        save_content[keys[i]] = localStorage.getItem(keys[i]);
      }
      let filename = "export_favorite_" + utils.get_current_time_f() + ".json"
      utils.download_text_as_file(JSON.stringify(save_content), filename);
    },
    async importFavClick() {
      this.menu_more_is_shown = false;

      function _check(o) {
        if (typeof o === "undefined") {
          throw new Error("object is undefined");
        }
      }

      try {
        let fav_json = await utils.get_file_content(".json")
        fav_json = JSON.parse(fav_json)
        console.log(fav_json);

        // Check if is valid favorite
        let fav = {};
        let k0 = Object.keys(fav_json);
        console.log(k0)
        for (let i=0; i<k0.length; i++) {
          let fal = JSON.parse(fav_json[k0[i]]);

          // check for each item
          let falk = Object.keys(fal);
          for (let j=0; j < falk.length; j++) {
            let al = fal[falk[j]];
            // console.log(al)
            _check(al["al"])
            _check(al["name"])
            _check(al["h"])
            _check(al["w"])
            _check(al["ct"])
          }
        }

        for (let i=0; i<k0.length; i++) {
          let fal = fav_json[k0[i]];
          console.log("Import favorite: ", k0[i], fal)
          window.localStorage.setItem(k0[i], fal);
        }

        this.initialize(); // reload favorite
      }
      catch (ee) {
        console.log(ee);
        alert(this.tr("content.fav.unrecognized"));
      }

    }
  }
}

</script>

<style scoped>
.fav-btn {
  display: none;
  cursor: pointer;
}

.photo-mask:hover {
  background-color: rgba(0, 0, 0, 0.05);
}

.photo.box:hover >.fav-btn {
  display: block;
}

div.dialog-container {
  position: fixed;
  left: 0;
  right: 0;
  top: 0;
  height: 100%;
  width: 100%;
  z-index: 19999;
}

button.large_button {
  width: 100px;
}

button.primary_btn,
button.primary_btn:hover {
  border: 1px solid #5555ff;
  background-color: #5555ff;
}
button.primary_btn:active {
  border: 1px solid #000088 !important;
  background-color: #000088 !important;
}

pre.share_url {
  user-select: all;
  text-wrap: wrap;
  color: blue;
  background: #fff;
  padding: 10px;
  border-radius: 5px;
}
pre.share_url:hover {
  text-decoration: underline;
}

.cnav::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  backdrop-filter: blur(2px);
  mask: linear-gradient(to bottom,
            rgba(0, 0, 0, 1) 0%, rgba(0, 0, 0, 0.9) 50% ,rgba(0, 0, 0, 0) 100%);
  pointer-events: none;
}

@media screen and (max-width: 500px) {
  button.large_button {
    width: 100%;
  }

  button.primary_btn,
  pre.share_url {
    background-color: transparent;
    border: 1px solid #fff;
    border-top: 1px solid #eee;
    border-bottom: 1px solid #eee;
    border-radius: 0;
    color: #000 !important;
    padding-left: 15px !important;
    height: 40px !important;
    text-align: left;
    color: #5555ff !important;
  }
  button.primary_btn:hover {
    border: 1px solid #eee !important;
    background-color: #eee !important;
  }
  button.primary_btn:active {
    border: 1px solid #ddd !important;
    background-color: #ddd !important;
  }

  .mbutton-group {
    border-radius: 6px;
  }
}
</style>