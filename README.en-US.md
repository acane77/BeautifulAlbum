

# Beautiful Album

## Introduction

This is a pure static online album styled like iOS.

<a href="https://acane77.github.io/album-demo.html" STYLE="font-size: 18px">Online Demo</a> (Password is `secret`)

* Pure static webpage, requires no backend programs or databases during runtime, and can be hosted on GitHub Pages (github.io).
* Supports multiple albums with password protection for access.

## Chao Yue Mei Mei is absolutely adorable!!!

![Preview for PC](docs/pc_prev.png)

![Preview for PC](docs/pc.png)

![Image Preview UI](docs/image_prev.png)

<img src="docs/mobile.png" height="768px"/>

## How to Use?

**Use the `bootstrap.sh` script to automatically build and compile the website project and generate the relevant APIs.**

**Note**:
* Windows users need to run this script using msys2, git-bash, or WSL2.
* It is recommended to use Node.js version 16.
    * It is recommended to use `nvm` to manage the Node.js environment: run `nvm use 16` to switch to version 16.

**Step 1. Organize Albums**

Create a new directory anywhere to serve as the album directory, for example, `~/my_album`.

Within this album directory, organize your albums according to the following rules:

1. Each subdirectory represents an album. It is recommended to use English names, e.g., `cutecy`.
2. Create a `.txt` file with the same name as the directory to define a custom display name. For example, create `cutecy.txt` and save the text you want to display as the album name in the UI (e.g., `Chao Yue Mei Mei is so cute`).
3. You can place any images inside each album's directory. 

An organized directory structure looks like this:

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

**Step 2. Run the Script**

The script will check for required environments and dependencies. If any dependencies are missing, you will need to install them manually.

* Pass the target directory where you want to generate the APIs via the `--prefix` parameter, e.g., `/mnt/data/wwwroot`.
* Pass the album directory created in the previous step via the `--album-dir` parameter, e.g., `~/my_album`.

Common usage examples are as follows:

* Build the project, generate APIs, and create an album with password `1234`:
```bash
./bootstrap.sh --center-face \
               --password=1234 \
               --prefix=/mnt/data/wwwroot \
               --album-dir=~/my_album
```

* Skip project build, only regenerate APIs (suitable for updating albums):
```bash
./bootstrap.sh --generate-api-only \
               --center-face \
               --password=1234 \
               --prefix=/mnt/data/wwwroot \
               --album-dir=~/my_album
```

* Only build the project, skip API regeneration (suitable for updating the program):
```bash 
./bootstrap.sh --build-webpage-only \
               --center-face \
               --password=1234 \
               --prefix=/mnt/data/wwwroot \
               --album-dir=~/my_album
```

* For more parameters and features, please refer to the help documentation:
```bash
usage: ./bootstrap.sh [OPTIONS] ...

Options:
    --prefix=PREFIX        Specify the location to generate the final packaged program files and API documentation
    --album-dir=DIR        Specify the album directory (see structure details below)
    --center-face          Perform face detection to center faces in the main interface preview, see detailed instructions below
    --face-detector=DETECTOR_NAME  
                           Specify the inference frontend for face detection, see detailed instructions below
    --face-detector-model=MODEL_NAME
                           Specify the model for face detection, see detailed instructions below
    --face-clustering      Generate APIs required for the "People" feature, see detailed instructions below
    --password=PWD         Specify the album password
    --build-webpage-only   Only build the website project, do not generate APIs
    --generate-api-only    Do not build the project, only regenerate APIs (suitable for updating albums)
    --copy-resource        Do not rebuild the website, but copy the compiled website project files to the directory specified by --prefix
    --python-path=NAME     Specify the location of the python command, default: python
    --disable-cache        Do not use cache when generating thumbnails, regenerate all
    --install-deps         Install npm dependencies, equivalent to running 'npm build' in the project directory
    --disable-share        Disable the "Share" feature, do not generate related APIs
    --use-symlink          Use symbolic links instead of copying files when generating APIs for the "Share" feature
    --help, -h             Show help information
    --                     All arguments after -- will be passed to 'scripts/generate_api.py'
```

### Example: Face Detection using deepface and yolov8

```bash
docker run -d -p 8080:8080 \
  -v /path/to/your/album:/www/album \
  -e ALBUM_PASSWORD=secret \
  -e CENTER_FACE=1 \
  -e FACE_DETECTOR=deepface \
  -e FACE_DETECTOR_MODEL=yolov8 \
  beautiful-album
```

### Example: Enable Face Clustering Feature

```bash
docker run -d -p 8080:8080 \
  -v /path/to/your/album:/www/album \
  -e ALBUM_PASSWORD=secret \
  -e CENTER_FACE=1 \
  -e FACE_DETECTOR=deepface \
  -e FACE_DETECTOR_MODEL=yolov8 \
  -e FACE_CLUSTERING=1 \
  beautiful-album
```

---

**Face Centering Feature: Face Detection Instructions**

The available inference frontends are listed below. You can specify them using the `--face-detector` parameter, and use `--face-detector-model` to specify the model to use.

* [opencv](https://github.com/opencv/opencv): Directly obtain the model XML file using `git submodule update --init --recursive`.
* [deepface](https://github.com/serengil/deepface): Install using `pip install deepface`. It defaults to using the `yolov8` backend for face detection. If missing packages are prompted during runtime, install them as instructed.

Using the deepface backend allows leveraging CUDA for face recognition (faster).

For example, to generate APIs using face detection with deepface and yolov8, run the following command:
```bash 
./bootstrap.sh --generate-api-only \
               --center-face \
               --password=1234 \
               --prefix=/mnt/data/wwwroot \
               --album-dir=~/my_album \
               --face-detector=deepface --face-detector-model=yolov8
```

**"People" Classification Feature Instructions**

Using the people classification feature (via the `--face-clustering` parameter) can extract photos of the same person from all images "as much as possible" to form a category. Only `deepface` can be used as the inference framework for people classification.

```bash
./bootstrap.sh --generate-api-only \
               --center-face \
               --password=1234 \
               --prefix=/mnt/data/wwwroot \
               --album-dir=~/my_album \
               --face-detector=deepface --face-detector-model=yolov8 \
               --face-clustering 
```

Specify custom clustering parameters:

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

## Deploy with Docker

### Organize Albums

* Refer to "Step 1. Organize Albums" above.

### Container Directory Explanation

* **Web Files**: `/www/` directory inside the container
* **Album Directory**: `/www/album/` directory inside the container (needs to be mounted to the host's album directory)
* **API Files**: `/www/api/` directory inside the container (auto-generated)

### Basic Usage

**1. Build the Docker Image**

```bash
docker build -t beautiful-album .
```

**2. Run the Container**

```bash
docker run -d -p 8080:8080 \
  -v /path/to/your/album:/www/album \
  beautiful-album
```

After running, wait for the API build to complete, then visit `http://localhost:8080` to view the album.

### Customize Configuration with Environment Variables

The Docker container supports configuring project parameters via environment variables:

```bash
docker run -d -p 8080:8080 \
  -v /path/to/your/album:/www/album \
  -e ALBUM_PASSWORD=yourpassword \
  -e CENTER_FACE=1 \
  -e FACE_DETECTOR=deepface \
  -e FACE_DETECTOR_MODEL=yolov8 \
  -e FACE_CLUSTERING=1 \
  beautiful-album
```

### Accelerate API Generation with GPU in Docker

If the host has an NVIDIA GPU and NVIDIA Container Toolkit installed, you can use the GPU to accelerate face feature detection during face detection and clustering, significantly improving processing speed.

```bash
docker run -d -p 8080:8080 \
  --gpus all \
  -v /path/to/your/album:/www/album \
  -e ALBUM_PASSWORD=yourpassword \
  -e CENTER_FACE=1 \
  -e FACE_DETECTOR=deepface \
  -e FACE_DETECTOR_MODEL=yolov8 \
  -e FACE_CLUSTERING=1 \
  beautiful-album
```

**Note:**
* Install the [NVIDIA Container Toolkit](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/install-guide.html) before deploying with GPU.
* GPU acceleration only works when using `deepface` as the face detector.
* Ensure Docker version is 19.03 or higher to support the `--gpus` flag.

### Environment Variables Explanation

* `ALBUM_PASSWORD`: Album password (default: `secret`)
* `CENTER_FACE`: Whether to enable face centering (set to `1` or `true` to enable)
* `FACE_DETECTOR`: Face detector (default: `opencv`, optional: `deepface`)
* `FACE_DETECTOR_MODEL`: Face detection model (e.g., `yolov8`, only required when using `deepface`)
* `FACE_CLUSTERING`: Whether to enable face clustering (set to `1` or `true` to enable)
* `DISABLE_SHARE`: Whether to disable the share feature (set to `1` or `true` to disable)
* `PORT`: Web server port (default: `8080`)

### Copy Built Files

If you need to copy the built files (including generated APIs) from the container to your local machine, you can use the `docker cp` command:

```bash
docker cp beautiful-album:/www /your/local/path
```

**Note**: 
* `beautiful-album` is the container name or ID. If running in the background with `-d`, check the container name or ID using `docker ps`.
* After copying, the `/your/local/path/www` directory will contain all built files and can be directly deployed to a web server.

---------

by Miyuki, 2020.1, Licensed under MIT license
