<template>
  <div  style="height: 100%; overflow-y: auto" @scroll="handleScroll">
    <div class="cnav">
      <div :class="['title', 'left', sidebar_shown_pc?'':'sidebar-hidden']">
        <span class="title-text">{{ album_friendly_name }}</span>
      </div>
      <div class="title right">
        <span style="color: #eee; margin-right: 10px;">{{ photo_count }}张图片</span>
        <button>共享</button>

      </div>
      <div class="back left"   style="line-height:45px; left: 18px; top: 0" @click="raise_event_show_sidebar(true, 'mobile')">
        <i class="larrow" style="border-color: white"></i><span class="backtext">照片</span>
      </div>

      <div :class="['back', 'left', 'sidebar-hidden-left', sidebar_shown_pc?'':'sidebar-hidden']" @click="raise_event_show_sidebar(true, 'pc')" style="line-height:45px; left: 18px; top: 0">
        <span class="backtext">显示</span>
      </div>
    </div>

    <div>
      <div class="photo box" v-for="(photo, i) in photo_list" :photo-name="photo.name" :key="i" :style="{ backgroundImage: `url('${ get_thumbnail_image(photo.al, photo.name) }')` }"
            @click="raise_event_show_preview(photo.name, photo_list, i, photo.al, photo)"
      >
      </div>
    </div>
  </div>
</template>

<script>
//import IDMapping from "@/js/IDMapping";
import '../css/style.css'
import '../css/contentview.css'

import utils from "@/js/utils";
const PHOTO_PER_PAGE = 50;

export default {
  name: "Content",
  components: {},
  props: [ 'base_name', 'album_friendly_name', 'sidebar_shown_pc' ],
  data() {
    return {
      page_count: 0,
      current_page_to_load: 0,
      photo_count: 0,
      photo_list: [],
      initial_scroll_height: 0,
      response_load_new: true,
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
    },
  },
  watch: {
    base_name() {
      this.initialize();
    }
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
      this.photo_list.push(...await utils.get_secured_json(this.album_get_image_at_current_page_json_name));
      this.current_page_to_load++;
    },
    get_thumbnail_image(alumn_name ,image_name) {
      return "/api/album-cache/" + alumn_name + "/" + image_name;
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
      this.photo_count = (await utils.get_secured_json(this.album_get_count_json_name)).count;
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
    }
  }
}

</script>

<style scoped>

</style>