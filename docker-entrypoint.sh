#!/bin/bash

# Entrypoint script: Check album directory and generate APIs (if needed), then start server

set -e

WWW_DIR="/www"
ALBUM_DIR="${WWW_DIR}/album"
BOOTSTRAP_SCRIPT="/build/bootstrap.sh"
TIMESTAMP_FILE="${WWW_DIR}/TIMESTAMP"

echo "=== Beautiful Album Docker Entrypoint ==="

cd /build

# Check if album directory exists
if [ -d "$ALBUM_DIR" ] && [ "$(ls -A $ALBUM_DIR 2>/dev/null)" ]; then
    echo "-- Album directory found: $ALBUM_DIR"
    
    # Check if we need to regenerate APIs by comparing timestamps
    NEED_REGENERATE=true
    if [ -f "$TIMESTAMP_FILE" ]; then
        # Get modification time of album directory and timestamp file
        ALBUM_MTIME=$(stat -c %Y "$ALBUM_DIR" 2>/dev/null || echo "0")
        TIMESTAMP_MTIME=$(stat -c %Y "$TIMESTAMP_FILE" 2>/dev/null || echo "0")
        
        # If album directory is older than timestamp, skip regeneration
        if [ "$ALBUM_MTIME" -lt "$TIMESTAMP_MTIME" ]; then
            echo "-- Album directory is up-to-date (timestamp: $TIMESTAMP_MTIME, album: $ALBUM_MTIME)"
            echo "-- Skipping API regeneration..."
            NEED_REGENERATE=false
        else
            echo "-- Album directory has been modified, regenerating APIs..."
        fi
    else
        echo "-- Timestamp file not found, generating APIs..."
    fi
    
    if [ "$NEED_REGENERATE" = true ]; then
        echo "-- Generating APIs..."
    
    # Build arguments (can be passed via environment variables)
    CENTER_FACE_ARG=""
    FACE_DETECTOR="${FACE_DETECTOR:-opencv}"
    FACE_DETECTOR_MODEL_ARG=""
    FACE_CLUSTERING_ARG=""
    DISABLE_SHARE_ARG=""
    PASSWORD="${ALBUM_PASSWORD:-secret}"
    
    if [ "${CENTER_FACE:-}" == "1" ] || [ "${CENTER_FACE:-}" == "true" ]; then
        CENTER_FACE_ARG="--center-face"
    fi
    
    if [ -n "${FACE_DETECTOR_MODEL:-}" ]; then
        FACE_DETECTOR_MODEL_ARG="--face-detector-model=${FACE_DETECTOR_MODEL}"
    fi
    
    if [ "${FACE_CLUSTERING:-}" == "1" ] || [ "${FACE_CLUSTERING:-}" == "true" ]; then
        FACE_CLUSTERING_ARG="--face-clustering"
    fi
    
    if [ "${DISABLE_SHARE:-}" == "1" ] || [ "${DISABLE_SHARE:-}" == "true" ]; then
        DISABLE_SHARE_ARG="--disable-share"
    fi
    
    # Generate APIs (only generate APIs, do not rebuild webpage)
    # Build command array, only add non-empty arguments
    CMD_ARGS=(
        --generate-api-only
        --prefix="$WWW_DIR"
        --album-dir="$ALBUM_DIR"
        --password="$PASSWORD"
        --face-detector="$FACE_DETECTOR"
    )
    
    [ -n "$CENTER_FACE_ARG" ] && CMD_ARGS+=("$CENTER_FACE_ARG")
    [ -n "$FACE_DETECTOR_MODEL_ARG" ] && CMD_ARGS+=("$FACE_DETECTOR_MODEL_ARG")
    [ -n "$FACE_CLUSTERING_ARG" ] && CMD_ARGS+=("$FACE_CLUSTERING_ARG")
    [ -n "$DISABLE_SHARE_ARG" ] && CMD_ARGS+=("$DISABLE_SHARE_ARG")
    
        if "$BOOTSTRAP_SCRIPT" "${CMD_ARGS[@]}"; then
            echo "-- API generation completed!"
            # Update timestamp file after successful API generation
            touch "$TIMESTAMP_FILE"
            echo "-- Timestamp file updated: $TIMESTAMP_FILE"
        else
            echo "-- Error: API generation failed, but continuing to start server..."
        fi
    fi
else
    echo "-- Warning: Album directory not found or empty: $ALBUM_DIR"
    echo "-- Skipping API generation. Please mount your album directory to $ALBUM_DIR"
fi

echo "-- Starting web server on port ${PORT:-8080}..."
cd "$WWW_DIR"
exec http-server -p "${PORT:-8080}" --cors -c-1
