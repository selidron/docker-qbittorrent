# Qbittorrent Docker Image
#   by selidron

# Pull Alpine base
#FROM alpine:latest
FROM selidron/baseimage:av

# Define ARGS
#ARG uid=1000
#ARG gid=1000
#ARG tz='America/New_York'
#ARG umask=000
ARG webui_port=8080

# Set Environment Variables
#ENV uid=1000 \
#    gid=1000 \
#    tz='America/New_York' \
#    umask=000 \
ENV webui_port=8080

#RUN apk add --no-cache \
#    bash nano font-dejavu python3 py3-pip qt6-qtbase qt6-qtbase-sqlite clamav \
#    busybox-binsh libcrypto3 libgcc libstdc++ libtorrent-rasterbar musl zlib qbittorrent-nox
RUN apk add --no-cache \
    qt6-qtbase qt6-qtbase-sqlite libgcc libstdc++ libtorrent-rasterbar musl zlib qbittorrent-nox git

# Install qbittorrent-api
RUN pip install qbittorrent-api --break-system-packages

# Update virus database
#RUN chmod 777 /var/lib/clamav && freshclam

# Copy root to system
COPY root /

# Set scripts ownership and access
RUN chown root:root -R /python && chmod 755 -R /python

# Create defaults for user app (if UID and GID are provided as environment variable, init will change this)
#RUN adduser -HD -h /home -u 1000 app && chmod 777 -R /home

# Expose ports
EXPOSE 8080

# Modify PATH variable
ENV PATH="${PATH}:/python"

# Volumes
VOLUME /config

# Set entry point
ENTRYPOINT [ "/init" ]