#!/bin/bash

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

build_hash2album
