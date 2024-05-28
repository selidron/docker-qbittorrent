# Docker QBittorrent
Qbittorrent docker image source files containing methods to automatically update listening port, run AV scan on torrent completion, and copy files to a directory for processing.

## Implements
<a href=https://github.com/rmartin16/qbittorrent-api>Python qBittorrent API</a>

## Installation

### Docker Compose
There is a ready to deploy docker-compose.yaml available in the repository. It can used as it, though should be modified to fit your specific setup.

```yaml
services:
    qbittorrent:
        image: selidron/qbittorrent:latest
        container_name: qbittorrent
        network_mode: service:gluetun # If launched from the same compose file
        #network_mode: container:gluetun # If launched from separate compose files
        deploy:
            restart_policy:
                condition: any
                window: '15s'
                delay: '15s'
#            resources:
#                limits:
#                    cpus: 1.0
#                    memory: 8G
        environment:
        -   uid=1000
        -   gid=1000
        -   umask=000
        -   webui_port=8080         # Port to listen for WebUI traffic
            #Location to store the script's config file
        -   py_conf=/config/py.conf
            # Forwarded port check interval in seconds (10800=3 hrs)
        -   port_check_interval=10800
            # Location to find the port file from gluetun
        -   gluetun_port_file=/config/gluetun/forwarded_port
        # Uncomment the following if not using a container VPN
#        ports:
#        -   8080:8080
        volumes:
        # Modify these as you like to fit your set-up, these paths need to be set in QBittorrent config as well
        -   /downloads/dir:/downloading
        -   /completed/dir:/completed
        -   /seeding/dir:/seeding
        # This is for separating processing directories from download directories
        -   /process/dir:/process
        # This is an example of using a separate directory for the gluetun file
        -   /gluetun/forwarded_port/dir:/gluetun
        # This is required
        -   /config/dir:/config
```

<i><b>Something to Consider:</b> Whenever the gluetun container is restarted, the qBittorrent container will also need to be restarted, so it may desireable to keep them within the same compose file for ease of restarts.</i>

## Configuration
In order for the additional features of this image to function, some configurations are necessary.

### Environment Variables
|   Variable    |   Default |   Description |
|   :------     |   :------ |   :------     |
|   `uid`       |   `1000`  |   User ID to use to run qBittorrent   |
|   `gid`       |   `1000`  |   User Group ID to run qBittorrent |
|   `umask`     |   `000`   |   UMask to apply to file permissions<br>Not implemented yet.  |
|   `webui_port`|   `8080`  |   Port which the WebUI should be accessible from|
|   `port_check_interval`|   `10800` |   Seconds to check for port updates (Default: 3hrs)|
| `py_conf` | `/config/py.conf` | Location to store the configuration file for the scripts. |
| `gluetun_port_file` | `/config/gluetun/forwarded_port` | Location where Gluetun's forwarded_port file can be access. |

### Configuring the Scripts
The python .conf configuration file is located at ```/config/python/.conf```.

This is a minimal configuration. The file is made of the following fields:

- `copy`: Enable copying of files for processing. This is disabled by default, to prevent the scripts from running loose without proper configuration.

- ```exclude_from_copy```: This is a list of categories to exclude from copying to a process directory. AV scans will still be performed, though category management will not since it will serve no purpose with this script alone.

- ```repPath```: Temporary path for replicating files.

- ```destPath```: Destination path for files being copied.

- ```clamCheck```: <b>DO NOT MODIFY</b> - This field is just for keeping track of the last time the AV database was checked for update. The database will be checked once per day, prior to scanning files. This is utilised to limit the number of calls to the database server.
