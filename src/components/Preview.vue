<template>
  <div :class="showNavBar ? 'preview-with-navbar' : 'preview-hidden-navbar'" style="width: 100%; height: 100%;">
    <span style="position: absolute; top: 45%; text-align: center; color: #888; display: block; width: 100%;">正在加载图片...</span>
    <div class="preview-photo-base preview-bg" :style="{backgroundImage: 'url(\''+thumbnail_path+'\')', backgroundSize: getBackgroundSize() }"></div>
    <div class="preview-photo-high-res preview-bg" :style="{backgroundImage: 'url(\''+photo_path+'\')', backgroundSize: getBackgroundSize() }"></div>
    <div class="preview-mask" @click="() => { showNavBar = !showNavBar }"></div>
    <div class="navbar" style="width: 100% !important;" v-show="showNavBar">
      <div class="nav-title">
        {{ photo_name }}
      </div>
      <div class="left-button-group" @click="raise_hide_preview()">
        <i class="larrow"></i><span class="backtext">{{ catalog_name === '' ? '相册列表':catalog_name }}</span>
      </div>

      <div class="right-button-group">
        <a href="javascript:void(0)" @click="downloadPhoto()">下载</a>
      </div>


    </div>
  </div>
</template>

<script>
import '../css/style.css';
import '../css/preview.css';

export default {
  name: "Preview",
  props: [ 'current_album_name', 'current_photo_filename', 'image_list', 'index', 'catalog_name' ],
  data: () => ({
    showNavBar: true,
  }),
  computed: {
    photo_name() {
      return this.current_photo_filename.replace(/\.[a-z|A-Z|0-9]*$/g, "");
    },
    thumbnail_path() {
      return `/api/album-cache/${this.current_album_name}/${this.current_photo_filename}`;
    },
    photo_path() {
      return `/api/album/${this.current_album_name}/${this.current_photo_filename}`;
    },
    current_photo() {
      return this.image_list[this.index];
    }
  },
  methods: {
    raise_hide_preview() {
      this.$emit('hide-preview');
    },
    load_image() {

    },
    thumbnail_path_at_index(i) {
      return `/api/album-cache/${this.image_list[i].al}/${this.image_list[i].name}`;
    },
    photo_path_at_index(i) {
      return `/api/album/${this.image_list[i].al}/${this.image_list[i].name}`;
    },
    downloadPhoto() {
      window.open(this.photo_path);
    },
    getBackgroundSize() {
      //current_photo.h > current_photo.w ? 'auto 100%':'100% auto'
      let ph = this.current_photo.h;
      let pw = this.current_photo.w;
      let wh = window.innerHeight;
      let ww = window.innerWidth;
      let pr = pw / ph;
      let wr = ww / wh;
      let dr = pr - wr;
      const fill_width = 'auto 100%';
      const fill_height = '100% auto';
      if (pr > 1) { // 横屏
        if (wr > 1) { // 横图
          if (dr > 0) return fill_height;
          else return fill_width;
        }
        else { // 竖图
          return fill_height;
        }
      }
      else { // 竖屏
        if (wr > 1) { // 横图
          return fill_width;
        }
        else { // 竖图
          if (dr > 0) {
            return fill_height;
          }
          else fill_width;
        }
      }
    }
  },
  mounted() {

  },
}
</script>

<style scoped>

</style>