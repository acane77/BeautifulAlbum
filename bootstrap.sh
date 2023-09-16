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

Options:
    --prefix=PREFIX        Path to generate APIs, can be also used to update current file.
                             Default: $(pwd)/install
    --album-dir=DIR        Path to album directory, store the original images
                             Default: PREFIX/album
    --center-face          Perform face detection while generating API, to center the faces in
                           preview mode.
    --password=PWD         Password for accessing the album
    --build-webpage-only   Only build webpage, do not generate APIs
    --generate-api-only    Only generate APIs
    --copy-resource        Copy built website resources to PREFIX directory
    --python-path=NAME     Specify path to python3 binary
                             Default: python
    --disable-cache        Do not use cache when generating thumbnails
    --install-deps         Install npm deps
    --help, -h             Print this help message and exit
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
      elif [ "$KEY" == "--password" ]; then
        F_PASSWORD="$1"
      elif [ "$KEY" == "--copy-resource" ]; then
        CONFIG_COPY_RES=1
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
}

function check_for_env() {
  echo "-- Checking environment for building..."
  check_npm_installed
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

function build_website() {
  if [ "$CONFIG_GENERATE_API_ONLY" != "" ]; then
    return 0;
  fi
  if [ "$CONFIG_INSTALL_DEPS" != "" ]; then
    echo "-- Installing NPM deps ..."
    npm install
    __assert "install NPM deps failed"
  fi
  echo "-- Building website..."
  npm run build
  __assert "build NPM website failed"
  echo "-- Build succeed!"
  copy_website_files
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
  $PYTHON generate_api.py $F_CENTER_FACE $F_PASSWORD
  __assert "API generate failed"
  rm ../third_party
  echo "-- API Generated!"
  cd "$__CURRENT_DIR"
}

function main() {
  parse_args $*
  check_for_env
  build_website
  if [ "$CONFIG_COPY_RES" != "" ]; then
    copy_website_files
  fi
  build_api

  echo "-- All finished! "
  echo "To have a quick preview, run"
  echo "    $ npm install -g http-server"
  echo "    $ http-server $CONFIG_PREFIX"
}

main $*