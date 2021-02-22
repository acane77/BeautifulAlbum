<template>
  <div :class="showNavBar ? 'preview-with-navbar' : 'preview-hidden-navbar'" style="width: 100%; height: 100%;">
    <span style="position: absolute; top: 45%; text-align: center; color: #888; display: block; width: 100%;">正在加载图片...</span>
    <div class="preview-photo-base preview-bg" :style="{backgroundImage: 'url(\''+thumbnail_path+'\')', backgroundSize: current_photo.h > current_photo.w ? 'auto 100%':'100% auto' }"></div>
    <div class="preview-photo-high-res preview-bg" :style="{backgroundImage: 'url(\''+photo_path+'\')', backgroundSize: current_photo.h > current_photo.w ? 'auto 100%':'100% auto' }"></div>
    <div class="preview-mask" @click="() => { showNavBar = !showNavBar }"></div>
    <div class="navbar" style="width: 100% !important;" v-show="showNavBar">
      <div class="nav-title">
        {{ photo_name }}
      </div>
      <div class="left-button-group" @click="raise_hide_preview()">
        <i class="larrow"></i><span class="backtext">相册列表</span>
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
  props: [ 'current_album_name', 'current_photo_filename', 'image_list', 'index' ],
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
    }
  },
  mounted() {

  },
}
</script>

<style scoped>

</style>