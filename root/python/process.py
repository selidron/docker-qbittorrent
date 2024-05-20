import os
import sys
import subprocess
import shutil
import datetime
import time
import json
from threading import Thread
from hashlib import md5
from pathlib import Path
from qbt import QBt
from Config import Config
from Config import Config

separator = '---------------------'

class Process:
    def __init__(self,
            dry: bool = False,
            skipscan: bool = False
    ) -> None:
        self.qbt: QBt = QBt()
        self.config: Config = Config()
        self.config._load()

        # Run parametres
        self.config.dry = dry
        self.config.dry = dry
        self.config.skipScan = skipscan

        self.srcPath: Path

        # Update clamscan
        if self.config.clamUpdated.date() < datetime.date.today():
            subprocess.run(['freshclam'])
            self.config.update_clam()
            print(f'\n{separator}\n')

        if self.config.dry: print('Dry run enabled, no changes will be made.')
        pass

    def set_port(self):
        port = int(open('/config/gluetun/forwarded_port').read())
        self.qbt.set_port(port)
        self.exit()

    def exit(self):
        self.qbt.exit()
        quit()

    def auto(self) -> None:
        self.qbt.get_torrents(progress=1.0)

        # Iterate through torrents and process
        for torrent in self.qbt.torrents:
            self.qbt.torrent = torrent
            self.srcPath = Path(self.qbt.torrent.save_path)
            self.process(torrent.hash)

    def process(self, hash) -> None:
        # Set torrent is not set
        if not self.qbt.torrent:
            self.qbt.get_torrent(hash)

        # Extract information from torrent
        name = self.qbt.torrent.name
        inputPath = self.qbt.torrent.content_path
        category = self.qbt.torrent.category
        # Process with supplied information
        print(f'Beginning processing of {name}...')
        print(f'Hash: {hash}')
        print(separator)

        try:
            if (not self.config.skipScan and not self.config.dry and
                not "scanned" in self.qbt.get_tags()):
                print('Beginning AV scan...')
                self.scan(inputPath)
            else:
                print('AV Scan Skipped.')
        except RuntimeError as e:
            print(f'AV Scan failed:\n{e}')
            print(separator)
            print('Terminating processing...')
            self.exit()
        
        if category in self.config.excludeCategories:
            print('Category is in excluded list, skipping file replication.')
            self.exit()
        
        if not self.config.copy:
            print('File replication is disabled.')
            self.exit()
        
        print(separator)
        print('Replicating file(s)...')
        inputPath = Path(inputPath)
        if inputPath.is_dir():
            self.replicate_dir(inputPath, name)
        else:
            self.replicate_file(inputPath,
                                self.config.repPath.joinpath(inputPath.name),
                                self.config.dstPath.joinpath(inputPath.name),
                                True)
        print('Finished replicating files.')
        self.clean_dir(self.config.repPath)
        print(separator)

        # Change torrent category
        self.qbt.set_category(self.config.seedCategory)
        self.qbt.clear_tags()
    
    def scan(self, path) -> bool | Exception:
        process_args=['/usr/bin/clamscan', '-r', '--remove', path]
        process = subprocess.Popen(process_args, stdout=subprocess.PIPE)
        stdout, stderr = process.communicate()
        process.wait()

        lines = stdout.splitlines()
        for line in lines: print(str(line, 'utf-8'))
        if process.returncode == 0:
            self.qbt.add_tag("scanned")
            return True
        else:
            raise RuntimeError(
                f'Clamscan returned none 0 return code: {process.returncode}\n'
                f'Stderr: {stderr.splitlines()}'
                )

    def replicate_dir(self, path, name) -> bool | Exception:
        # Set initial path variables
        path = Path(path)
        process = self.config.repPath
        dest = self.config.dstPath
        replicatedfiles = list()

        # Check for subdirectories and change paths accordingly
        dirs = [file for file in path.glob('*') if file.is_dir()]
        print(dirs)
        if len(dirs) > 0:
            print('Processing into subdirectory.')
            process = self.config.repPath.joinpath(name)
            dest = self.config.dstPath.joinpath(name)

        # Collect files to replicate
        files = [file for file in path.rglob('*') if file.is_file()]
        
        # Begin copying files
        for file in files:
            # Calculate paths
            relpath = os.path.relpath(str(file), str(path))
            fileprocess = process.joinpath(relpath)
            filedest = dest.joinpath(relpath)
            
            # Copy file and process if failed
            if not self.replicate_file(file, fileprocess):
                if (self.config.interactive and input(
                    'Replication failed, continue processing? (y/n)').casefold() == 'n'):
                    if input('Delete already replicated files? (y/m): ').casefold() == 'y':
                        for rfile in replicatedfiles:
                            os.remove(rfile)
                    self.exit()
            else:
                # Add file to replicated files
                replicatedfiles.append([fileprocess, filedest])
        
        # Move replicated files to destination directory
        for file in replicatedfiles:
            self.move_file(file[0], file[1])

    def replicate_file(self, src, proc: Path, dest = None, move: bool = False) -> bool:
        print(f'Replicating {src}...')
        proc.parent.mkdir(parents=True, exist_ok=True)
        src_size = os.path.getsize(src)
        copy_thread = Thread(target=shutil.copy, args=(src, proc))
        copy_thread.start()

        # Print progress of the copy
        if self.config.interactive:
            while True:
                time.sleep(1)
                dest_size = os.path.getsize(proc)
                progress = dest_size/src_size
                print(f"\r{progress:.2%}", end="")

                if progress >= 1.0:
                    copy_thread.join()
                    break
        else:
            copy_thread.join()
            
        shutil.copy(src, proc)
        os.chmod(proc, 0o777)

        # Compare hashes
        print('\rCalculating MD5 Hashes...')
        srcHash = self.get_hash(src)
        procHash = self.get_hash(proc)
        if srcHash == procHash:
            print(f'{srcHash} == {procHash}')
            if not move:
                return True
        else:
            print(f'{srcHash} != {procHash}')
            print('Removing replication attempt...')
            os.remove(proc)
            return False
        
        # Move replicated file
        self.move_file(proc, dest)
    
    def copy(self, src, dest):
        shutil.copy(src, dest)
    
    def move_file(self, src: Path, dest: Path):
        print('Beginning to move files...', end="")
        print(f'\r{src} --> {dest}', end='')
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.move(src, dest)
        print(f'\r{src} moved.', end="")

    def get_relative_path(self, path: Path) -> str:
        if path.is_file():
            path = path.parent
        return os.path.relpath(path, self.srcPath)

    def get_hash(self, path) -> str:
        """Return the MD5 hash of the requested file"""
        hash = md5()
        with open(path, 'rb') as f:
            while True:
                buffer = f.read(2**20)
                if not buffer:
                    break
                hash.update(buffer)
        return hash.hexdigest()

    def clean_dir(self, path):
        subprocess.run(['find', str(path), '-type', 'd', '-empty', '-delete'])
