from qbittorrentapi import Client,LoginFailed,TorrentDictionary,TorrentPropertiesDictionary
from TorrentFile import TorrentFile as File

class TorrentDataFailed(Exception):
    pass

class QBt:
    def __init__(self) -> None:
        self.client = Client(host="localhost", port=8037)
        self.torrents:list = list()
        self.torrent: TorrentDictionary = None
        self.files: list[File] = list()

        self.seeding: str = "seeding"
        try:
            self.client.auth_log_in()
        except LoginFailed as e:
            raise LoginFailed(e)
        pass

    def exit(self):
        self.client.auth_log_out
    
    def set_port(self, port: int):
        self.client.app.setPreferences({"listen_port": port})

    def get_torrents(self, category: str = "", progress: float = 0.0) -> None:
        torrents = self.client.torrents.info(category=category)
        for torrent in torrents:
            if torrent.progress >= progress:
                # Unless category is seeding, remove seeding torrents
                if category.casefold() != self.seeding and torrent.category.casefold() != self.seeding:
                    self.torrents.append(torrent)

    def get_torrent(self, hash):
        try:
            self.torrent = (self.client.torrents.info(torrent_hashes=[hash]))[0]
            for file in self.torrent.files:
                self.files.append(File(file.name))
            return True
        except Exception as e:
            raise TorrentDataFailed(f'Unable to retrieve torrent: {e}')
        pass

    def get_category(self):
        return self.torrent.category
    
    def set_category(self, category):
        try:
            self.torrent.set_category(category=category)
        except Exception as e:
            raise TorrentDataFailed(f'Failed to set category: {e}')
        pass

    def add_tag(self, tag: str):
        try:
            self.torrent.add_tags([tag])
        except Exception as e:
            raise TorrentDataFailed(f'Failed to add tag {tag}: {e}')
        
    def get_tags(self):
        return self.torrent.tags
    
    def clear_tags(self):
        print('Removing tags from torrent...')
        #for tag in self.torrent.tags:
        #    self.torrent.remove_tags([tag])
        self.torrent.remove_tags(self.torrent.tags)

