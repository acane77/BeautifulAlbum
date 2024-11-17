<template>
  <div style="padding-left: 10px; padding-right: 10px; height: 100%; overflow-y: auto" @scroll="handleScroll">
    <div :class="['navbar', shouldShowSemiTransparentNavBar ? '' : 'large']">
      <div class="nav-title">
        {{ tr("Photos") }}
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
      {{ tr("Photos") }}
    </div>

    <div class="listview normal-menu-ui" style="margin-top: 5px;">
      <a v-show="show_banner"  :class="get_css_class_list_item('/all')"
         @click="on_switch_album('/all', tr('sidebar.photo_library'))"
         href="javascript:void(0)">
        <span> {{ tr("sidebar.photo_library") }} </span>
      </a>
      <a v-show="show_banner" :class="get_css_class_list_item('/recent')"
         @click="on_switch_album('/recent', tr('sidebar.recent'))"
         href="javascript:void(0)"><span>{{ tr('sidebar.recent') }}</span>
      </a>
      <a :class="get_css_class_list_item('/fav')"
         @click="on_switch_album('/fav', tr('sidebar.favorites'))"
         href="javascript:void(0)"><span>{{ tr('sidebar.favorites') }}</span>
      </a>
    </div>

    <div class="title2">
      {{ tr("My Albums") }}
    </div>
    <div class="listview">
      <a :class="[ 'album-prev', get_css_class_list_item(album.name) ]" @click="on_switch_album(album.name, album.friendly_name)"  href="javascript:void(0)" v-for="album in album_list" :key="album.name">
        <div style="position: relative">
          <div class="list_img" :style="{ backgroundImage: album.preview==='' ? '':'url(\'/api/album-cache/' + album.name + '/' + album.preview + '\')' }"></div>
          <span style="margin-left: 27px;">{{ album.friendly_name }}</span>
        </div>

      </a>
    </div>

    <div class="title2" v-show="people_enabled && people_categories.length > 0">
      {{ tr("People") }}
    </div>
    <div class="people-list" v-show="people_enabled && people_categories.length > 0">
      <div :class="[ 'people', get_css_class_list_item('/people/category-' + cata.id) ]" :key="cata.id"
           :style="{
              backgroundImage: 'url(\'/api/album-cache/' + cata.preview.al + '/' + cata.preview.name + '\')',
              backgroundPosition: calcCenterFaceBgpos(cata.preview)
           }"
           @click="on_switch_album('/people/category-' + cata.id, tr('sidebar.people.title', cata.id + 1))"
           v-for="cata in people_categories">
      </div>
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
  props: [ "people_enabled" ],
  data: () => ({
    album_list: [],
    selected_album_name: '/all',
    show_banner: true,

    shouldShowSemiTransparentNavBar: false,
    people_categories: [],
  }),
  methods: {
    tr(x, ...args) { return utils.translate(x, ...args) },
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

      if (this.people_enabled) {
        const people_categories = await utils.get_secured_json("people/categories");
        this.people_categories = people_categories.categories;
      }
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
    },
    calcCenterFaceBgpos(photo) {
      return utils.calc_center_face_bg_pos(photo);
    }
  }
}
</script>

<style scoped>

</style>