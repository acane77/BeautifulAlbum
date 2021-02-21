<template>
  <div style="padding-left: 10px; padding-right: 10px; height: 100%; overflow-y: auto">
    <div class="navbar large">
      <div class="nav-title">
        照片
      </div>
      <div class="left-button-group">
        <a href="javascript:void(0)">隐藏</a>
      </div>

      <div class="right-button-group">
        <a class="disabled" href="javascript:void(0)">编辑</a>
      </div>
    </div>

    <div class="title1 navtitle" style="margin-top: 50px">
      照片
    </div>

    <div class="listview" style="margin-top: 5px;">
      <a class="selected" href="javascript:void(0)"><span>图库</span></a>
      <a href="javascript:void(0)"><span>最近项目</span></a>
    </div>

    <div class="title2">
      我的相簿
    </div>
    <div class="listview">
      <a href="javascript:void(0)" v-for="album in album_list" :key="album"><span>{{ album.friendly_name }}</span></a>
    </div>
  </div>
</template>

<script>
import '../css/style.css';
import utils from "@/js/utils";

export default {
  name: "Sidebar",
  data: () => ({
    album_list: []
  }),
  methods: {

  },
  async mounted() {
    this.album_list = await utils.get_json('get-album')

  }
}
</script>

<style scoped>

</style>