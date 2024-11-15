#!/bin/bash

#function check_build_env() {
#  ;
#}

__CURRENT_DIR="$PWD"
__PROG="$0"

function verbose() {
  if [ "$CONFIG_VERBOSE" != "" ]; then
    echo $*
  fi
}

function __assert() {
  ret=$?
  if [ $ret -ne 0 ]; then
    echo "error: $*"
    exit $ret
  fi
}

function __exit() {
  false
  __assert $*
}

function print_help() {
  cat <<EOF
usage: $__PROG [OPTIONS] ...

Common Options for Installation
    --prefix=PREFIX        Path to generate APIs, can be also used to update current file.
                             Default: $(pwd)/install
    --album-dir=DIR        Path to album directory, store the original images
                             Default: PREFIX/album

Options for Building Project
    --build-webpage-only   Only build webpage, do not generate APIs
    --release              Make a tar.gz package for built project to release

Options for Generating APIs
    --generate-api-only    Only generate APIs
    --center-face          Perform face detection while generating API, to center the faces in
                           preview mode.
    --face-detector=DETECTOR_NAME
                           Specify face detector for inference, for list of face detectors,
                           see README.md. Default: opencv
    --face-detector-model=MODEL_NAME
                           Specify face detector model, for detailed list of accepted values,
                           see README.md.
    --face-clustering      Generate "People" APIs (need parameter search for best performance)
    --password=PWD         Password for accessing the album
    --copy-resource        Copy built website resources to PREFIX directory
    --disable-cache        Do not use cache when generating thumbnails
    --disable-share        Disable share album API
    --use-symlink          Generate share API using symbolic link instead of copying files

Options for Environment
    --python-path=NAME     Specify path to python3 binary
                             Default: python
    --install-deps         Install npm deps

Other Options
    --help, -h             Print this help message and exit

Environment Variables
    NPM_FLAGS              Append arguments when invoke 'npm install' command.

EOF
}

function parse_args() {
    while [ "$1" != "" ]; do
      KEY="$(echo "$1"|cut -f 1 -d '=')"
      if [ "$KEY" == "--prefix" ]; then
        CONFIG_PREFIX="${1:9}"
      elif [ "$KEY" == "--album-dir" ]; then
        CONFIG_ALBUM_DIR="${1:12}"
      elif [ "$KEY" == "--build-webpage-only" ]; then
        CONFIG_BUILD_WEBPAGE_ONLY=1
      elif [ "$KEY" == "--generate-api-only" ]; then
        CONFIG_GENERATE_API_ONLY=1
      elif [ "$KEY" == "--python-path" ]; then
        CONFIG_PYTHON_PATH="${1:14}"
      elif [ "$KEY" == "--disable-cache" ]; then
        CONFIG_DISABLE_CACHE=1
      elif [ "$KEY" == "--install-deps" ]; then
        CONFIG_INSTALL_DEPS=1
      elif [ "$KEY" == "--center-face" ]; then
        F_CENTER_FACE="--center_face"
      elif [ "$KEY" == "--face-detector" ]; then
        F_FACE_DETECTOR="--face_detector=${1:16}"
        CONFIG_FACE_DETECTOR_BACKEND="${1:16}"
      elif [ "$KEY" == "--face-clustering" ]; then
        F_FACE_CLUSTERING="--face_clustering"
      elif [ "$KEY" == "--face-detector-model" ]; then
        F_FACE_DETECTOR_MODEL="--face_detector_model=${1:22}"
      elif [ "$KEY" == "--disable-share" ]; then
        F_DISABLE_SHARE="--disable_share"
      elif [ "$KEY" == "--use-symlink" ]; then
        USE_SYMLINK=1
      elif [ "$KEY" == "--password" ]; then
        F_PASSWORD="$1"
      elif [ "$KEY" == "--copy-resource" ]; then
        CONFIG_COPY_RES=1
      elif [ "$KEY" == "--release" ]; then
        CONFIG_RELEASE=1
      elif [ "$KEY" == "--help" ] || [ "$KEY" == "-h" ]; then
        print_help
        exit 0
      else
        __exit "invalid argument: $KEY, type '$__PROG -h' for help"
      fi
      shift
    done
}

function check_npm_installed() {
  if [ "$CONFIG_GENERATE_API_ONLY" != "" ]; then
    return 0;
  fi
  echo "-- Checking for NPM..."
  which npm 1>/dev/null 2>&1
  __assert "npm is not install. Please install NodeJS first"
  echo "-- Found NPM version: $(npm --version)"
}

function check_for_python_deps() {
  echo "-- Checking python dep: $2 ..."
  python -c "import $1" 1>/dev/null 2>&1
  __assert "missing python requirement: $2"
  echo "-- Checking python dep: $2   FOUND"
}

function check_python_dep_installed() {
  if [ "$CONFIG_BUILD_WEBPAGE_ONLY" != "" ]; then
    return 0
  fi
  if [ "$CONFIG_PYTHON_PATH" == "" ]; then
    CONFIG_PYTHON_PATH=python
  fi
  PYTHON="$CONFIG_PYTHON_PATH"
  echo "-- Checking for python..."
  which $CONFIG_PYTHON_PATH 1>/dev/null 2>&1
  __assert "python is not installed, please install python3"
  PYTHON_VERSION="$($CONFIG_PYTHON_PATH --version)"
  echo "-- Found Python version: $PYTHON_VERSION"
  PYTHON_VERSION="$(echo "$PYTHON_VERSION"|cut -f 2 -d ' '|cut -f 1 -d '.')"
  if [ "$PYTHON_VERSION" != "3" ]; then
    __exit "python3 is required"
  fi
  check_for_python_deps PIL   Pillow
  check_for_python_deps cv2   OpenCV
  check_for_python_deps numpy NumPy
  if [[ "$CONFIG_FACE_DETECTOR_BACKEND" == "deepface" ]]; then
    check_for_python_deps deepface deepface
  fi
}

function check_for_env() {
  echo "-- Checking environment for building..."
  if [ -f package.json ]; then
    check_npm_installed
  fi
  check_python_dep_installed

  # Check install prefix
  if [ "$CONFIG_PREFIX" == "" ]; then
    CONFIG_PREFIX="$(pwd)/install"
  fi
  if [ ! -d "$CONFIG_PREFIX" ]; then
    mkdir -p "$CONFIG_PREFIX"
    __assert "Cannot create directory: $CONFIG_PREFIX"
  fi
  echo "-- Installation prefix: $CONFIG_PREFIX"

  if [ "$CONFIG_BUILD_WEBPAGE_ONLY" != "" ]; then
    echo "-- Build project only, will not check for album"
    return 0
  fi

  # Check album list
  if [ "$CONFIG_ALBUM_DIR" == "" ]; then
    CONFIG_ALBUM_DIR="$CONFIG_PREFIX/album"
  fi
  if [ ! -d "$CONFIG_ALBUM_DIR" ]; then
    __exit "no such album directory: $CONFIG_ALBUM_DIR"
  fi
  echo "-- Album directory: $CONFIG_ALBUM_DIR"

  CONFIG_ALBUMS_LIST="$(ls -l "$CONFIG_ALBUM_DIR"|grep -Ei "^d"|awk '{ print $9 }')"
  CONFIG_ALBUMS_COUNT=0
  for album in $CONFIG_ALBUMS_LIST ; do
    echo "-- Found album: $album"
    CONFIG_ALBUMS_COUNT=$((CONFIG_ALBUMS_COUNT+1))
    # TODO: Check album name is all English
  done
  if [ "$CONFIG_ALBUMS_COUNT" == "0" ]; then
    __exit "No albums found"
  fi

  # Copy images if album directory is not in PREFIX
  if [ "$CONFIG_PREFIX/api/album" != "$CONFIG_ALBUM_DIR" ]; then
    echo "-- Copying images to install directory"
    mkdir -p "$CONFIG_PREFIX/api/"
    cp -r "$CONFIG_ALBUM_DIR" "$CONFIG_PREFIX/api/album"
  fi
}

function copy_website_files() {
  echo "-- Copying built website resources ..."
  cp -r dist/* "$CONFIG_PREFIX/"
}

function build_release_package() {
  if [ "$CONFIG_RELEASE" == "" ]; then
    return;
  fi
  echo "-- Building package for release ..."
  RELEASE_DATE="$(date "+%Y%m%d")"
  PRODUCT_PREFIX=BeautifulAlbum
  COMMIT_ID="$(git rev-parse --short HEAD)"
  RELEASE_NAME="${PRODUCT_PREFIX}-${COMMIT_ID}-${RELEASE_DATE}"
  rm -rf ./$RELEASE_NAME
  mkdir -p $RELEASE_NAME
  mkdir -p $RELEASE_NAME/scripts

  ## Copy resources into package
  cp -r dist $RELEASE_NAME/
  cp $__PROG $RELEASE_NAME/
  cp ./scripts/*.py $RELEASE_NAME/scripts/
  cp README.md $RELEASE_NAME/
  cp LICENSE $RELEASE_NAME/
  FACE_DETECT_MODEL="$(cat scripts/face_detect.py |grep face_detection_config|grep third_party|head -1|grep -oEi "third_party.*?xml")"
  mkdir -p $RELEASE_NAME/$(dirname "$FACE_DETECT_MODEL")
  cp $FACE_DETECT_MODEL $RELEASE_NAME/$(dirname "$FACE_DETECT_MODEL")/

  ## Make package
  zip -ry $RELEASE_NAME.zip $RELEASE_NAME
  __assert "make package failed"
  rm -rf ./$RELEASE_NAME
  echo "-- Package built: $(realpath RELEASE_NAME.zip)"
}

function build_website() {
  if [ "$CONFIG_GENERATE_API_ONLY" != "" ]; then
    return 0;
  fi
  if [ ! -f package.json ]; then
    echo "-- Already a production package, no need to build"
    copy_website_files
    return 0;
  fi
  if [ "$CONFIG_INSTALL_DEPS" != "" ] || [ ! -d node_modules ]; then
    echo "-- Installing NPM deps ..."
    npm install $NPM_FLAGS
    __assert "install NPM deps failed"
  fi
  echo "-- Building website..."
  npm run build
  __assert "build NPM website failed"
  echo "-- Build succeed!"
  copy_website_files
}

function build_hash2album() {
  if [ "$F_DISABLE_SHARE" != "" ]; then
    return 0
  fi
  while read line; do
    HASH_="$(echo "$line"|cut -f 1 -d ":")"
    ALBUM_="$(echo "$line"|cut -f 2 -d ":")"
    echo "-- Creating alias for album: $ALBUM_, hash: $HASH_"
    mkdir -p "shared/album" "shared/album-cache"
    if [ "$USE_SYMLINK" != "" ]; then
      ln -s "../album/$ALBUM_" "shared/album/$HASH_"
      ln -s "../album-cache/$ALBUM_" "shared/album-cache/$HASH_"
    else
      cp -r "album/$ALBUM_" "shared/album/$HASH_"
      cp -r "album-cache/$ALBUM_" "shared/album-cache/$HASH_"
    fi
  done <<EOF
$(cat hash2album.txt)
EOF

  rm -rf hash2album.txt
}

function build_api() {
  if [ "$CONFIG_BUILD_WEBPAGE_ONLY" != "" ]; then
    return 0
  fi

  echo "-- Copying python scripts ..."
  cp scripts/*.py "$CONFIG_PREFIX/api"
  cd "$CONFIG_PREFIX/api"

  if [ "$CONFIG_DISABLE_CACHE" != "" ]; then
    echo "-- Clean image thumbnail cache ..."
    rm -rf album-cache
  fi

  echo "-- Building APIs ..."
  if [ ! -e ../third_party ]; then
    ln -s "$__CURRENT_DIR/third_party" ../third_party
  fi
  $PYTHON generate_api.py $F_CENTER_FACE $F_DISABLE_SHARE $F_PASSWORD $F_FACE_DETECTOR $F_FACE_DETECTOR_MODEL \
          $F_FACE_CLUSTERING
  __assert "API generate failed"
  if [ ! -d ../third_party ]; then
    rm ../third_party
  fi
  echo "-- API Generated!"

  build_hash2album

  cd "$__CURRENT_DIR"
}

function main() {
  parse_args $*
  check_for_env
  build_website
  # Copy resources if specified or if in production mode
  if [ "$CONFIG_COPY_RES" != "" ] || [ ! -f package.json ]; then
    copy_website_files
  fi
  build_release_package
  build_api

  echo "-- All finished! "
  echo "To have a quick preview, run"
  echo "    $ npm install -g http-server $NPM_FLAGS"
  echo "    $ http-server $CONFIG_PREFIX"
}

main $*
