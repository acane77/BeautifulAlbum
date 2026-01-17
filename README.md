# Beautiful Album

## 简介

这是一个iOS风格的纯静态在线相册。

<a href="https://acane77.github.io/album-demo.html" STYLE="font-size: 18px">在线Demo</a> (密码为`secret`)

* 纯静态网页，运行时不需要任何后端程序和数据库，可存放在github.io。
* 支持多个相册，访问时支持密码保护


## 超越妹妹真的太可爱啦！！！

![Preview for PC](docs/pc_prev.png)

![Preview for PC](docs/pc.png)

![Image Preview UI](docs/image_prev.png)

<img src="docs/mobile.png" height="768px"/>

## 如何使用？

**使用bootstrap.sh脚本自动化构建编译网站项目以及生成相关API。**

**注意**：
* Windows用户需要使用msys2，git-bash或者WSL2运行这个脚本。
* NodeJS版本建议使用node 16版本。
    * 建议使用nvm管理node环境：运行`nvm use 16`切换到node 16版本。

**Step 1. 组织相册**

在任意地方新建一个一个目录，作为相册目录，例如 `~/my_album`

在这个相册目录下，按照下面的规则组织相册：

1. 每一个子目录都是一个相册，建议使用英语名，例如：`cutecy`。
2. 新建一个和之前的目录名同名的.txt文件可以自定义一个好看的名称。例如新建`cutecy.txt`，并在该文件中保存文本作为显示在界面中的相册名（例如：`超越妹妹可可爱爱`）。
3. 在每个相册的目录都可以放入任意的图片。 

一个组织好的目录结构如下

``` 
~/my_album
├── cutecy
│   ├── 1.jpg
│   └── 2.jpg
├── cutecy.txt
├── photos
│   ├── IMG_0001.jpg
│   └── IMG_0002.jpg
└── photos.txt
```

**Step 2. 运行脚本**

脚本会检查所需要的环境和依赖，如果提示缺少依赖，需要手动安装。

* 通过 `--prefix` 参数传入你想要生成API的目标目录，例如 `/mnt/data/wwwroot`
* 通过 `--album-dir` 参数传入上面步骤创建的相册目录，例如 `~/my_album`

常用的使用方法如下：

* 编译项目，并生成API，创建一个密码为1234的相册
```bash
./bootstrap.sh --center-face \
               --password=1234 \
               --prefix=/mnt/data/wwwroot \
               --album-dir=~/my_album
```

* 不编译项目，只重新生成API（适用于更新相册）
```bash
./bootstrap.sh --generate-api-only \
               --center-face \
               --password=1234 \
               --prefix=/mnt/data/wwwroot \
               --album-dir=~/my_album
```

* 只编译项目，不重新生成API（适用于更新程序）
```bash 
./bootstrap.sh --build-webpage-only \
               --center-face \
               --password=1234 \
               --prefix=/mnt/data/wwwroot \
               --album-dir=~/my_album
```

* 更多参数和功能请参考帮助说明
```bash
usage: ./bootstrap.sh [OPTIONS] ...

Options:
    --prefix=PREFIX        指定生成最终打包的程序文件和API文档的位置
    --album-dir=DIR        指定相册的目录（具体结构见下方说明）
    --center-face          做人脸检测，以使人脸居中显示在主界面预览中，见下方详细说明
    --face-detector=DETECTOR_NAME  
                           指定用于人脸检测的推理前端，见下方详细说明
    --face-detector-model=MODEL_NAME
                           指定用于人脸检测的模型，见下方详细说明
    --face-clustering      生成“人物”功能所需API，见下方详细说明
    --password=PWD         指定相册的密码
    --build-webpage-only   只编译网站项目，不生成API
    --generate-api-only    不编译项目，只重新生成API（适用于更新相册）
    --copy-resource        不重新编译网站，但是复制编译好的网站项目文件到--prefix指定的目录
    --python-path=NAME     指定python命令的位置，默认：python
    --disable-cache        在生成缩略图的时候不使用缓存，全部重新生成
    --install-deps         安装npm依赖，相当于在项目目录运行 'npm build'
    --disable-share        禁用“分享”功能，不生成相关的API
    --use-symlink          生成用于“分享”功能的API时，使用符号链接而不是拷贝文件
    --help, -h             显示帮助信息
    --                     -- 后面所有的参数将被传递给'scripts/generate_api.py'
```

**人脸居中功能：人脸检测说明**

可用的推理前端包括以下几种，可使用 `--face-detector` 参数传入，可用 `--face-detector-model` 指定要使用的模型。

* [opencv](https://github.com/opencv/opencv)：直接使用 `git submodule update --init --recursive`获取模型xml文件。
* [deepface](https://github.com/serengil/deepface)：使用 `pip install deepface` 安装，默认使用 `yolov8`后端进行人脸检测。在运行时如提示缺少包可以按照提示安装。

使用deepface后端可以利用CUDA进行人脸识别（更快）。

例如，使用deepface和yolov8进行人脸检测生成API，可执行下面的命令
```bash 
./bootstrap.sh --generate-api-only \
               --center-face \
               --password=1234 \
               --prefix=/mnt/data/wwwroot \
               --album-dir=~/my_album \
               --face-detector=deepface --face-detector-model=yolov8
```

**“人物”分类功能说明**

使用人物分类功能（使用`--face-clustering`参数）可以将所有照片中同一个人的照片“尽可能地”提取出来形成一个分类。进行人物分类时仅可使用 deepface 作为推理框架。

```bash
./bootstrap.sh --generate-api-only \
               --center-face \
               --password=1234 \
               --prefix=/mnt/data/wwwroot \
               --album-dir=~/my_album \
               --face-detector=deepface --face-detector-model=yolov8 \
               --face-clustering 
```

指定自定义的聚类参数

```bash
./bootstrap.sh --generate-api-only \
               --center-face \
               --password=1234 \
               --prefix=/mnt/data/wwwroot \
               --album-dir=~/my_album \
               --face-detector=deepface --face-detector-model=yolov8 \
               --face-clustering \
               -- --face_clustering_eps=0.75 --face_clustering_min_samples=4
```

---------

by Miyuki, 2020.1, Licensed under MIT license
