FROM ubuntu:22.04

# Set non-interactive installation
ENV DEBIAN_FRONTEND=noninteractive

# Set working directory
WORKDIR /build

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    git \
    wget \
    python3 \
    python3-pip \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install Node.js 16 (using NodeSource official repository)
RUN curl -fsSL https://deb.nodesource.com/setup_16.x | bash - \
    && apt-get install -y nodejs \
    && rm -rf /var/lib/apt/lists/*

# Verify Node.js version
RUN node --version && npm --version

# Install Python dependencies (including deepface for advanced face detection)
RUN pip3 install --no-cache-dir \
    Pillow \
    opencv-python \
    numpy \
    deepface

# Copy project files (.dockerignore will exclude unnecessary files)
COPY . /build

# Set executable permission for bootstrap.sh
RUN chmod +x /build/bootstrap.sh

# Create target directories
RUN mkdir -p /www /www/album

# Build webpage only, do not generate APIs (APIs will be generated at runtime based on mounted album directory)
RUN /build/bootstrap.sh \
        --build-webpage-only \
        --prefix=/www \
        --install-deps \
        || exit 1

# Install http-server for serving static website
RUN npm install -g http-server

# Copy entrypoint script
COPY docker-entrypoint.sh /docker-entrypoint.sh
RUN chmod +x /docker-entrypoint.sh

# Expose port
EXPOSE 8080

# Set working directory to /www
WORKDIR /www

# Use entrypoint script to start
ENTRYPOINT ["/docker-entrypoint.sh"]
