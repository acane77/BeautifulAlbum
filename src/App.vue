<template>
  <div>
    <div :class="['content-container', sidebar_shown_on_pc_mode?'':'side-hidden-screen']">
      <ContentView :base_name="contentAlbumName" :album_friendly_name="contentFriendlyName"
                   @should-show-sidebar="(val, mode) =>  mode === 'mobile' ? sidebar_shown_on_mobile_mode = val : sidebar_shown_on_pc_mode = val"
                   :sidebar_shown_pc = "sidebar_shown_on_pc_mode"
      ></ContentView>
    </div>
    <div class="sidebar-mobile-mask" v-show="sidebar_shown_on_mobile_mode" @click="sidebar_shown_on_mobile_mode = false"></div>
    <div :class="['sidebar-container', sidebar_shown_on_pc_mode?'':'side-hidden-screen', sidebar_shown_on_mobile_mode?'sidebar-mobile-shown':'']">
      <Sidebar @switch-album="(album_name, friendly_name) => { this.contentAlbumName = album_name; this.contentFriendlyName = friendly_name; }"
               @should-show-sidebar="(val, mode) =>  mode === 'mobile' ? sidebar_shown_on_mobile_mode = val : sidebar_shown_on_pc_mode = val"
      ></Sidebar>
    </div>
  </div>
</template>

<script>
import Sidebar from "@/components/Sidebar";
import ContentView from "@/components/Content";

export default {
  name: 'App',
  components: {
    Sidebar, ContentView
  },
  data: () => ({
    activeName: 'beautiful-album',
    content_view_shown: true,
    sidebar_shown_on_mobile_mode: false,
    sidebar_shown_on_pc_mode: true,

    contentAlbumName: "/all",
    contentFriendlyName: "图库",
  }),
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
  width: 20%;
  height: 100%;
  background: aliceblue;
  min-width: 200px;
}
.content-container {
  position: fixed;
  top: 0;
  right: 0;
  display: inline-block;
  width: 80%;
  background: #fff;
  min-width: 500px;
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

@media screen and (max-width: 1200px) {
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
</style>
