# Qbittorrent Docker Image
#   by selidron

# Pull Alpine base
FROM selidron/baseimage:av

ENV webui_port=8080 \
    py_conf=/config/py.conf \
    port_check_interval=10800

# Install additional packages and tools
RUN apk add --no-cache \
    qt6-qtbase qt6-qtbase-sqlite libgcc libstdc++ libtorrent-rasterbar musl zlib qbittorrent-nox git

# Install qbittorrent-api
RUN pip install qbittorrent-api --break-system-packages

# Copy root to system
COPY root /

# Set scripts ownership and access
RUN chown root:root -R /python && chmod 755 -R /python

# Expose ports
EXPOSE 8080

# Modify PATH variable
ENV PATH="${PATH}:/python"