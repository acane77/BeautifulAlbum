<template>
  <div style="padding-left: 10px; padding-right: 10px; height: 100%; overflow-y: auto" @scroll="handleScroll">
    <div :class="['navbar', shouldShowSemiTransparentNavBar ? '' : 'large']">
      <div class="nav-title">
        照片
      </div>
      <div class="left-button-group">
        <a class="hidden-btn" href="javascript:void(0)"
           @click="() => {
             this.raise_event_show_sidebar(false, 'mobile');
             this.raise_event_show_sidebar(false, 'pc') }">
          <IconBase icon-color="#5555ff"> <IconSideBar /> </IconBase>
        </a>
      </div>

      <div class="right-button-group">
        <a href="javascript:void(0)" @click="logout()"> <IconBase icon-color="#5555ff" height="21"> <IconExit /> </IconBase> </a>
      </div>
    </div>

    <div class="title1 navtitle" :style="{ marginTop: '50px', opacity: 1-shouldShowSemiTransparentNavBar }">
      照片
    </div>

    <div class="listview normal-menu-ui" style="margin-top: 5px;">
      <a v-show="show_banner"  :class="get_css_class_list_item('/all')" @click="on_switch_album('/all', '图库')" href="javascript:void(0)"><span>图库</span></a>
      <a v-show="show_banner"  :class="get_css_class_list_item('/recent')" @click="on_switch_album('/recent', '最近项目')" href="javascript:void(0)"><span>最近项目</span></a>
      <a :class="get_css_class_list_item('/fav')" @click="on_switch_album('/fav', '个人收藏')" href="javascript:void(0)"><span>个人收藏</span></a>
    </div>

    <div class="title2">
      我的相簿
    </div>
    <div class="listview">
      <a :class="[ 'album-prev', get_css_class_list_item(album.name) ]" @click="on_switch_album(album.name, album.friendly_name)"  href="javascript:void(0)" v-for="album in album_list" :key="album.name">
        <div style="position: relative">
          <div class="list_img" :style="{ backgroundImage: album.preview==='' ? '':'url(\'/api/album-cache/' + album.name + '/' + album.preview + '\')' }"></div>
          <span style="margin-left: 27px;">{{ album.friendly_name }}</span>
        </div>

      </a>
    </div>
  </div>
</template>

<script>
import '../css/style.css';
import '../css/sidebar.css';
import '../css/mobile_optimize.css'
import '../css/dark_theme.css'
import utils from "@/js/utils";
import IconBase from "@/icons/IconBase";
import IconSideBar from "@/icons/IconSideBar";
import IconExit from "@/icons/IconExit";

export default {
  name: "Sidebar",
  components: {IconSideBar, IconBase, IconExit},
  data: () => ({
    album_list: [],
    selected_album_name: '/all',
    show_banner: true,

    shouldShowSemiTransparentNavBar: false,
  }),
  methods: {
    raise_event_show_sidebar(val, mode) {
      this.$emit('should-show-sidebar', val, mode);
    },
    on_switch_album(album_name, album_friendly_name) {
      this.$emit('switch-album', album_name, album_friendly_name);
      this.selected_album_name = album_name;
      if (window.innerWidth <= 1200) {
        this.raise_event_show_sidebar(false, 'mobile');
      }
    },
    get_css_class_list_item(album_name) {
      return album_name === this.selected_album_name ? "selected" : "";
    },
    handleScroll: function(el) {
      console.log((el.srcElement.scrollTop));
      if((el.srcElement.scrollTop) >= 30) {
        this.shouldShowSemiTransparentNavBar = true;
      }
      else {
        console.log('ttt');
        this.shouldShowSemiTransparentNavBar = false;
      }
    },
    async getAlbumList() {
      this.album_list = await utils.get_secured_json('get-album')
    },
    async getAlbumListForShare(album_hash) {
      window.share_album_hash = album_hash;
      let album_info = { name: "/share", friendly_name: "共享的相册", preview: "" };
      this.album_list = [ album_info ];
      this.show_banner = false;
      this.on_switch_album(album_info["name"], album_info["friendly_name"]);
    },
    logout() {
      localStorage.removeItem('password');
      location.reload();
    }
  }
}
</script>

<style scoped>

</style>