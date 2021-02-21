<template>
  <div>
    <div class="sidebar-container" v-show="sidebar_shown">
      <Sidebar></Sidebar>
    </div>
    <div class="content-container" v-show="content_view_shown">
      <ContentView :base_name="contentAlbumName"></ContentView>
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
    sidebar_shown: true,
    content_view_shown: true,

    contentAlbumName: "/all",
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

@media screen and (max-width: 1200px) {
  .sidebar-container {
    display: none;
  }
  .content-container {
    width: 100%;
  }
}
</style>
