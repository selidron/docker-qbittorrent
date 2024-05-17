# Dockerfile for qbittorrent by selidron
# Built using baseimages:
#		https://github.com/jlesage/docker-baseimage-gui (pending)
#       https://github.com/linuxserver/docker-qbittorrent

# Pull base image(s)
#FROM jlesage/baseimage-gui:alpine-3.19-v4
FROM lscr.io/linuxserver/qbittorrent:latest

# Install additional packages
RUN apk add font-dejavu python3 py3-pip qt6-qtbase-sqlite clamav

# Install python3 qbittorrent-api
RUN pip install qbittorrent-api --break-system-packages

# Clone rootfs to system
COPY rootfs /

# Set name of the application
#RUN set-cont-env APP_NAME "qbittorrent" # Needed for J leSages base

# Update virus database (not working)
#RUN wget -P /var/lib/clamav http://database.clamav.net/main.cvd
RUN chmod 777 /var/lib/clamav && freshclam

# Expose ports
EXPOSE 8080 6881 6881/udp

# Volumes
VOLUME /config

# Copy base python scripts to config
COPY src/python /config/python
