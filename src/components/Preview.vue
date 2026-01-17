<template>
  <div :class="showNavBar ? 'preview-with-navbar' : 'preview-hidden-navbar'" style="width: 100%; height: 100%; position: relative; overflow: hidden;">
    <!-- Canvas 容器 -->
    <div class="canvas-container" 
         @mousedown="handleMouseDown"
         @mousemove="handleMouseMove"
         @mouseup="handleMouseUp"
         @mouseleave="handleMouseUp"
         @wheel="handleWheel"
         @click="handleCanvasClick"
         ref="canvasContainer">
      <canvas ref="canvas" :width="canvasWidth" :height="canvasHeight"></canvas>
    </div>
    
    <!-- 顶部导航栏 -->
    <div class="navbar" style="width: 100% !important;" v-show="showNavBar">
      <div class="nav-title">
        {{ photo_name }}
      </div>
      <div class="left-button-group" @click="raise_hide_preview()">
        <i class="larrow"></i><span class="backtext">{{ catalog_name === '' ? tr("Album"):catalog_name }}</span>
      </div>

      <div class="right-button-group">
        <a href="javascript:void(0)" @click="downloadPhoto()">{{ tr("preview.download_btn") }}</a>
      </div>
    </div>
    
    <!-- 缩放工具栏 -->
    <div class="zoom-toolbar" v-show="showNavBar">
      <button class="zoom-btn" @click="zoomIn" :disabled="scale >= maxScale" :title="tr('preview.zoom_in')">
        <span style="font-size: 18px;">+</span>
      </button>
      <button class="zoom-btn" @click="zoomOut" :disabled="scale <= minScale" :title="tr('preview.zoom_out')">
        <span style="font-size: 18px;">−</span>
      </button>
      <button class="zoom-btn" @click="resetZoom" :disabled="scale === initialScale && offsetX === initialOffsetX && offsetY === initialOffsetY" :title="tr('preview.reset_zoom')">
        <span style="font-size: 14px;">⟲</span>
      </button>
    </div>
  </div>
</template>

<script>
import '../css/style.css';
import '../css/preview.css';
import utils from "@/js/utils";

export default {
  name: "Preview",
  props: [ 'current_album_name', 'current_photo_filename', 'image_list', 'index', 'catalog_name', 'current_photo' ],
  data() {
    return {
      showNavBar: true,
      isLoading: true,
      canvasWidth: 0,
      canvasHeight: 0,
      image: null,
      thumbnail: null,
      scale: 1,
      minScale: 0.1,
      maxScale: 5,
      offsetX: 0,
      offsetY: 0,
      isDragging: false,
      dragStartX: 0,
      dragStartY: 0,
      dragStartOffsetX: 0,
      dragStartOffsetY: 0,
      dragEndX: undefined,
      dragEndY: undefined,
      initialScale: 1,
      initialOffsetX: 0,
      initialOffsetY: 0,
      isDarkMode: false
    }
  },
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
  },
  methods: {
    tr(x, ...args) { return utils.translate(x, ...args) },
    raise_hide_preview() {
      this.$emit('hide-preview');
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
    updateCanvasSize() {
      if (this.$refs.canvasContainer) {
        const rect = this.$refs.canvasContainer.getBoundingClientRect();
        this.canvasWidth = rect.width;
        this.canvasHeight = rect.height;
      } else {
        this.canvasWidth = window.innerWidth;
        this.canvasHeight = window.innerHeight;
      }
      this.$nextTick(() => {
        this.drawImage();
      });
    },
    calculateInitialTransform() {
      if (!this.current_photo) return;
      
      const imgWidth = this.current_photo.w;
      const imgHeight = this.current_photo.h;
      const canvasWidth = this.canvasWidth;
      const canvasHeight = this.canvasHeight;
      
      const scaleX = canvasWidth / imgWidth;
      const scaleY = canvasHeight / imgHeight;
      
      // 选择较小的缩放比例以保持宽高比并适应画布
      this.initialScale = Math.min(scaleX, scaleY, 1);
      
      // 居中显示（图片中心在画布中心）
      this.initialOffsetX = canvasWidth / 2;
      this.initialOffsetY = canvasHeight / 2;
      
      this.scale = this.initialScale;
      this.offsetX = this.initialOffsetX;
      this.offsetY = this.initialOffsetY;
    },
    async loadImages() {
      this.isLoading = true;
      
      // 确保 canvas 尺寸已更新
      this.updateCanvasSize();
      
      // 加载缩略图
      const thumbImg = new Image();
      thumbImg.crossOrigin = 'anonymous';
      thumbImg.onload = () => {
        this.thumbnail = thumbImg;
        if (!this.image && this.current_photo) {
          // 如果高清图还没加载，使用缩略图计算初始变换
          this.calculateInitialTransform();
        }
        this.drawImage();
      };
      thumbImg.onerror = () => {
        console.error('Failed to load thumbnail:', this.thumbnail_path);
      };
      thumbImg.src = this.thumbnail_path;
      
      // 加载高清图
      const img = new Image();
      img.crossOrigin = 'anonymous';
      img.onload = () => {
        this.image = img;
        this.isLoading = false;
        this.calculateInitialTransform();
        this.drawImage();
      };
      img.onerror = () => {
        this.isLoading = false;
        console.error('Failed to load image:', this.photo_path);
        // 如果高清图加载失败，使用缩略图
        if (this.thumbnail) {
          this.drawImage();
        }
      };
      img.src = this.photo_path;
    },
    checkDarkMode() {
      // 检测系统主题偏好
      const darkModeMediaQuery = window.matchMedia('(prefers-color-scheme: dark)');
      this.isDarkMode = darkModeMediaQuery.matches;
      return this.isDarkMode;
    },
    drawImage() {
      const canvas = this.$refs.canvas;
      if (!canvas) return;
      
      const ctx = canvas.getContext('2d');
      ctx.clearRect(0, 0, canvas.width, canvas.height);
      
      // 根据系统主题设置背景色
      this.checkDarkMode();
      ctx.fillStyle = this.isDarkMode ? '#000000' : '#ffffff';
      ctx.fillRect(0, 0, canvas.width, canvas.height);
      
      if (!this.image && !this.thumbnail) return;
      
      const imgToDraw = this.image || this.thumbnail;
      if (!imgToDraw || !this.current_photo) return;
      
      ctx.save();
      
      // 移动到图片中心位置
      ctx.translate(this.offsetX, this.offsetY);
      // 应用缩放
      ctx.scale(this.scale, this.scale);
      
      // 绘制图片（以图片中心为基准）
      const imgWidth = this.current_photo.w;
      const imgHeight = this.current_photo.h;
      ctx.drawImage(
        imgToDraw,
        -imgWidth / 2,
        -imgHeight / 2,
        imgWidth,
        imgHeight
      );
      
      ctx.restore();
    },
    zoomIn() {
      this.scale = Math.min(this.scale * 1.2, this.maxScale);
      this.drawImage();
    },
    zoomOut() {
      this.scale = Math.max(this.scale / 1.2, this.minScale);
      this.drawImage();
    },
    resetZoom() {
      this.scale = this.initialScale;
      this.offsetX = this.initialOffsetX;
      this.offsetY = this.initialOffsetY;
      this.drawImage();
    },
    handleWheel(e) {
      e.preventDefault();
      const canvas = this.$refs.canvas;
      if (!canvas) return;
      
      const delta = e.deltaY > 0 ? 0.9 : 1.1;
      const oldScale = this.scale;
      const newScale = Math.max(this.minScale, Math.min(this.scale * delta, this.maxScale));
      
      // 以鼠标位置为中心缩放
      const rect = canvas.getBoundingClientRect();
      const mouseX = e.clientX - rect.left;
      const mouseY = e.clientY - rect.top;
      
      // 计算缩放前后鼠标相对于图片中心的位置变化
      const scaleChange = newScale / oldScale;
      this.offsetX = mouseX - (mouseX - this.offsetX) * scaleChange;
      this.offsetY = mouseY - (mouseY - this.offsetY) * scaleChange;
      this.scale = newScale;
      
      this.drawImage();
    },
    handleMouseDown(e) {
      if (e.button === 0) { // 左键
        this.isDragging = true;
        this.dragStartX = e.clientX;
        this.dragStartY = e.clientY;
        this.dragStartOffsetX = this.offsetX;
        this.dragStartOffsetY = this.offsetY;
        // 重置拖拽结束位置
        this.dragEndX = e.clientX;
        this.dragEndY = e.clientY;
        e.preventDefault();
      }
    },
    handleMouseMove(e) {
      if (this.isDragging) {
        const deltaX = e.clientX - this.dragStartX;
        const deltaY = e.clientY - this.dragStartY;
        this.offsetX = this.dragStartOffsetX + deltaX;
        this.offsetY = this.dragStartOffsetY + deltaY;
        this.drawImage();
        e.preventDefault();
      }
    },
    handleMouseUp(e) {
      // 记录鼠标抬起位置，用于判断是否为点击而不是拖拽
      if (this.isDragging) {
        this.dragEndX = e.clientX;
        this.dragEndY = e.clientY;
      }
      this.isDragging = false;
    },
    handleCanvasClick(e) {
      // 只有在不是拖拽操作时才切换 navbar
      // 判断鼠标按下和抬起的位置是否相同（允许小范围误差）
      if (this.dragEndX !== undefined && this.dragEndY !== undefined) {
        const deltaX = Math.abs(this.dragStartX - this.dragEndX);
        const deltaY = Math.abs(this.dragStartY - this.dragEndY);
        // 如果移动距离小于 5 像素，认为是点击操作
        if (deltaX < 5 && deltaY < 5) {
          this.showNavBar = !this.showNavBar;
          this.$nextTick(() => {
            this.drawImage();
          });
        }
      }
      // 重置拖拽结束位置
      this.dragEndX = undefined;
      this.dragEndY = undefined;
    }
  },
  watch: {
    current_photo(newVal, oldVal) {
      if (newVal && newVal !== oldVal) {
        // 重置缩放和位置
        this.scale = 1;
        this.offsetX = 0;
        this.offsetY = 0;
        this.image = null;
        this.thumbnail = null;
        this.loadImages();
      }
    },
    showNavBar() {
      this.$nextTick(() => {
        this.drawImage();
      });
    }
  },
  mounted() {
    this.$nextTick(() => {
      this.updateCanvasSize();
      window.addEventListener('resize', this.updateCanvasSize);
      
      // 监听系统主题变化
      const darkModeMediaQuery = window.matchMedia('(prefers-color-scheme: dark)');
      const handleThemeChange = (e) => {
        this.isDarkMode = e.matches;
        this.drawImage();
      };
      darkModeMediaQuery.addEventListener('change', handleThemeChange);
      this.darkModeMediaQuery = darkModeMediaQuery;
      this.handleThemeChange = handleThemeChange;
      
      if (this.current_photo) {
        this.loadImages();
      }
    });
  },
  beforeDestroy() {
    window.removeEventListener('resize', this.updateCanvasSize);
    // 移除主题变化监听器
    if (this.darkModeMediaQuery && this.handleThemeChange) {
      this.darkModeMediaQuery.removeEventListener('change', this.handleThemeChange);
    }
  }
}
</script>

<style scoped>
.canvas-container {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  cursor: grab;
  background-color: #fff;
}

@media (prefers-color-scheme: dark) {
  .canvas-container {
    background-color: #000;
  }
}

.canvas-container:active {
  cursor: grabbing;
}

canvas {
  display: block;
  width: 100%;
  height: 100%;
}

.zoom-toolbar {
  position: absolute;
  bottom: 20px;
  left: 50%;
  transform: translateX(-50%);
  display: flex;
  gap: 10px;
  /* iOS风格毛玻璃效果 */
  background: rgba(255, 255, 255, 0.7);
  backdrop-filter: blur(20px) saturate(180%);
  -webkit-backdrop-filter: blur(20px) saturate(180%);
  border: 1px solid rgba(255, 255, 255, 0.18);
  box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.1);
  padding: 8px 12px;
  border-radius: 12px;
  z-index: 1000;
}

@media (prefers-color-scheme: dark) {
  .zoom-toolbar {
    background: rgba(0, 0, 0, 0.5);
    border: 1px solid rgba(255, 255, 255, 0.1);
    box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.3);
  }
}

.zoom-btn {
  background: rgba(255, 255, 255, 0.9);
  border: 1px solid rgba(255, 255, 255, 0.5);
  border-radius: 8px;
  width: 40px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  color: #333;
  font-size: 14px;
  transition: all 0.2s ease;
  box-shadow: 0 2px 8px 0 rgba(0, 0, 0, 0.1);
}

.zoom-btn:hover:not(:disabled) {
  background: rgba(255, 255, 255, 1);
  transform: scale(1.05);
  box-shadow: 0 4px 12px 0 rgba(0, 0, 0, 0.15);
}

.zoom-btn:active:not(:disabled) {
  transform: scale(0.95);
  box-shadow: 0 1px 4px 0 rgba(0, 0, 0, 0.1);
}

.zoom-btn:disabled {
  opacity: 0.4;
  cursor: not-allowed;
  background: rgba(255, 255, 255, 0.5);
}

@media (prefers-color-scheme: dark) {
  .zoom-btn {
    background: rgba(255, 255, 255, 0.15);
    border: 1px solid rgba(255, 255, 255, 0.2);
    color: #fff;
    box-shadow: 0 2px 8px 0 rgba(0, 0, 0, 0.3);
  }

  .zoom-btn:hover:not(:disabled) {
    background: rgba(255, 255, 255, 0.25);
    box-shadow: 0 4px 12px 0 rgba(0, 0, 0, 0.4);
  }

  .zoom-btn:disabled {
    background: rgba(255, 255, 255, 0.08);
  }
}

</style>