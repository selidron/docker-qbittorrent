from pathlib import Path
import os
import shutil
from hashlib import md5

class FileReplicationError(Exception):
    pass

class TorrentFile:
    def __init__(self, path: Path) -> None:
        self.src: Path = path
        self.process: Path = None
        self.dest: Path = None

        self.name: str = self.src.name
        self.src_md5: str = None
        self.dest_md5: str = None
        pass

    def set_paths(self, process: Path, dest: Path):
        self.process = process.joinpath(self.name)
        self.dest = dest.joinpath(self.name)
        pass

    def get_hash(self, path):
        """Return the MD5 hash of the requested file"""
        hash = md5()
        with open(path, 'rb') as f:
            while True:
                buffer = f.read(2**20)
                if not buffer:
                    break
                hash.update(buffer)
        return hash.hexdigest()

    def replicate(self):
        self.src_md5 = self.get_hash(self.src)
        shutil.copy(self.src, self.process)
        self.dest_md5 = self.get_hash(self.process)
        if self.src_md5 == self.dest_md5:
            return True
        else:
            os.remove(self.process)
            raise FileReplicationError('MD5 hashes do not match. Replication aborted.')
        pass
    