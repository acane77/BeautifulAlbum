<template>
  <div  style="height: 100%; overflow-y: auto" @scroll="handleScroll">
    <div class="cnav">
      <div :class="['title', 'left', sidebar_shown_pc?'':'sidebar-hidden']">
        <span class="title-text">{{ album_friendly_name }}</span>
      </div>
      <div class="title right">
        <span style="color: #eee; margin-right: 10px;">{{ photo_count }}张图片</span>
        <button @click="menu_more_is_shown = !menu_more_is_shown" style="">...</button>
        <!-- 弹出的菜单 -->
        <div class="context-menu-mask" v-show="menu_more_is_shown" @click="menu_more_is_shown = false"></div>
        <div :class="['context-menu', menu_more_is_shown?'shown':'hidden']" v-show="menu_more_is_shown" style="top: 56px; right: 20px">
          <a href="javascript:void(0)"
             @click="current_zoom_scale < 2 && ((current_zoom_scale++), (menu_more_is_shown = false))"
             :aria-disabled="current_zoom_scale >= 2">放大</a>
          <a href="javascript:void(0)"
             @click="current_zoom_scale > -6 && ((current_zoom_scale--), (menu_more_is_shown = false))"
             :aria-disabled="current_zoom_scale <= -6">缩小</a>
          <a href="javascript:void(0)"
             @click="current_zoom_scale != 0 && ((current_zoom_scale = 0), (menu_more_is_shown = false))"
             :aria-disabled="current_zoom_scale == 0">默认缩放 (当前：{{ current_zoom_scale }})</a>
          <hr />
          <a href="javascript:void(0)" aria-disabled="true">分享...</a>
          <hr v-show="base_name === '/fav'" />
          <a href="javascript:void(0)" aria-disabled="true" v-show="base_name === '/fav'">导出个人收藏</a>
          <a href="javascript:void(0)" aria-disabled="true" v-show="base_name === '/fav'">导入个人收藏</a>
        </div>

      </div>
      <div class="back left"   style="line-height:45px; left: 18px; top: 0" @click="raise_event_show_sidebar(true, 'mobile')">
        <i class="larrow" style="border-color: white"></i><span class="backtext">照片</span>
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

const PHOTO_PER_PAGE = 50;

export default {
  name: "Content",
  components: { IconSideBar, IconBase, IconHeart, IconHeartFilled },
  props: [ 'base_name', 'album_friendly_name', 'sidebar_shown_pc' ],
  data() {
    return {
      page_count: 0,
      current_page_to_load: 0,
      photo_count: 0,
      photo_list: [],
      initial_scroll_height: 0,
      response_load_new: true,
      fav_content_cache: {},
      fav_page_cache: null,
      // UI Element -- Menu
      menu_more_is_shown: false,
      current_zoom_scale: 0,
    }
  },
  computed: {
    album_common_prefix() {
      if (this.base_name === '/all')
        return 'get-photo-';
      if (this.base_name === '/recent')
        return 'get-recent-photo-';
      if (this.base_name === '/fav')
        return 'get-fav-photo-'; /// NOT: load from localstorage
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
    raise_event_show_sidebar(val, mode) {
      this.$emit('should-show-sidebar', val, mode);
    },
    raise_event_show_preview(image_file_name, photo_list, photo_index, album_name, photo_obj) {
      this.$emit('preview-photo', image_file_name, photo_list, photo_index, album_name, photo_obj);
    },
    async load_image() {
      if (!this.response_load_new) {
        return;
      }
      this.response_load_new = false;
      setTimeout(() => { this.response_load_new = true; }, 1000)
      if (this.current_page_to_load >= this.page_count)
        return;
      if (this.album_get_count_json_name.startsWith("get-fav-photo-")) {
        let max_i = Math.min(this.photo_list.length + PHOTO_PER_PAGE, this.fav_page_cache.length);
        for (let i=this.photo_list.length; i < max_i; i++) {
          this.photo_list.push(this.fav_page_cache[i]);
        }
      }
      else {
        this.photo_list.push(...await utils.get_secured_json(this.album_get_image_at_current_page_json_name));
        this.applyFavoriteWithPhotos(); // TODO: 性能优化：先执行着一条语句再加入photolist
      }

      this.current_page_to_load++;
    },
    get_thumbnail_image(alumn_name ,image_name) {
      return "/api/album-cache/" + alumn_name + "/" + image_name;
    },
    get_thumbnail_image_backgrouod_pos(photo) {
      // 如果没有开启人脸居中功能，即没有在生成API的时候做人脸检测，直接返回默认值
      if (typeof photo.faces == "undefined") {
        return '0px 0px';
      }
      let faces = photo.faces;
      // 如果没有检测到人脸
      if (faces.length == 0)
        return '0px 0px';

      // 根据所有的人脸框，求出人脸框平均值最大的位置
      let avg_x = faces.map(e => e[0]).reduce((a, b)=>a+b, 0) / faces.length;
      let avg_y = faces.map(e => e[1]).reduce((a, b)=>a+b, 0) / faces.length;
      let avg_w = faces.map(e => e[2]).reduce((a, b)=>a+b, 0) / faces.length;
      let avg_h = faces.map(e => e[3]).reduce((a, b)=>a+b, 0) / faces.length;

      // 图片平均中心点的位置
      let center_x = avg_x + avg_w / 2;
      let center_y = avg_y + avg_h / 2;

      let image_w = photo.w;
      let image_h = photo.h;

      // 根据图片的宽高比居中人脸
      let wh_ratio = photo.w / photo.h;
      if (wh_ratio > 1.0) {
        // 如果图片是横图
        let hw_ratio = photo.h / photo.w;
        let w_ratio = center_x / image_w;
        let ratio = Math.max(0, w_ratio - hw_ratio / 2);
        return `${ ratio * 100 }% 0%`
      }
      else {
        // 如果图片是竖图
        let h_ratio = center_y / image_h;
        let ratio = h_ratio; Math.max(0, h_ratio - wh_ratio / 2)
        return `0% ${ ratio * 100 }%`;
      }
      // return '1px 1px';
    },

    async initialize() {
      if (this.base_name === "")
        return;

      this.current_page_to_load = 0;
      this.photo_list = [];
      this.response_load_new = true;
      this.initial_scroll_height = 0;
      this.photo_count = this.page_count = 0;

      // get page count
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

        // console.log("-- Favorite album count:", this.photo_count);
      }
      else {
        this.photo_count = (await utils.get_secured_json(this.album_get_count_json_name)).count;
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
        alert('你的浏览器不支持Local Storage，无法使用此功能。');
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
</style>