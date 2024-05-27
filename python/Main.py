#!/usr/bin/python3

import argparse
import os
from pathlib import Path

import process

parser = argparse.ArgumentParser(description="QBittorrent download completion script.")
parser.add_argument('-c', '--category', metavar="", type=str,
                    help="Current QBittorrent category.")
parser.add_argument('--dryrun', action='store_true', default=False,
                    help="Dry run script to see what will happen.")
parser.add_argument('-g', '--gid', metavar="", type=int, default=1370,
                    help="GID to use for file and directory permissions.")
parser.add_argument("--hash", metavar="",
                    help="Torrent hash needed to identify torrent for modifications.")
parser.add_argument('-i', '--input', metavar="", type=str,
                    help="Input processing directory. (root_path in QBittorrent)")
parser.add_argument('-lv', '--loglevel', metavar="", type=str, default='WARNING',
                    help='Log level: DEBUG, INFO, WARNING, ERROR')
parser.add_argument('-m', '--manual', action='store_true',
                    help="Manual call to autonomously process all from QBt Client.")
parser.add_argument('-n', '--torrentname', metavar="", type=str, default="_",
                    help="Name of the torrent file in QBittorrent.")
parser.add_argument('-o', '--output', metavar="", type=str,
                    help="Final output directory of files. \nDefault is /process/")
parser.add_argument('-p', '--process', metavar="", type=str,
                    help="Directory to use for replication and processing.\nDefault is /process/.auto/replicate/")
parser.add_argument('--skipscan', action='store_true',
                    help="Skip ClamAV virus scan.")
parser.add_argument('-u', '--uid', metavar="", type=int, default=1370,
                    help="UID to use for file and directory permissions.")
parser.add_argument('--port', action='store_true',
                    help="Process port forwarding.")
args = parser.parse_args()

# Initialise UMASK
os.umask(os.environ['umask'])

# Initialise process object
process = process.Process(
    args.dryrun,
    args.skipscan
)
process.config.interactive = args.manual
if args.process: process.config.repPath = args.process
if args.output: process.config.dstPath = args.output
process.config.logLevel = args.loglevel

if args.port:
    process.set_port()
    pass
elif args.touch:
    t_file:os.path = os.path.abspath(args.touch)
    with open(t_file, 'w') as f:
        pass
elif args.hash:
    process.process(args.hash)
elif args.manual:
    process.auto()
else:
    process.process(args.hash)
