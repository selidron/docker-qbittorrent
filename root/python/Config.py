import datetime
import os
import json
from pathlib import Path

class Config:
    def __init__(self) -> None:
        # System
        self.file = Path(os.environ['py_conf']) if os.environ['py_conf'] else Path('/config/py.conf')
        self.clamUpdated: datetime.date
        self.logLevel: str

        # Processing
        self.interactive: bool
        self.dry: bool
        self.skipScan: bool
        self.copy: bool
        self.seedCategory: str
        self.excludeCategories: list
        self.srcPath: Path
        self.repPath: Path
        self.dstPath: Path
    
    def _load(self):
        if self.file.exists():
            with open(self.file, 'r') as f:
                data = json.loads(f.read())
        else:
            data = dict()
        
        self.clamUpdated = datetime.datetime.strptime(data.get("clamCheck", "2000-01-01"), "%Y-%m-%d")
        self.logLevel = data.get("logLevel", "INFO")
        self.copy = data.get("copy", False)
        self.seedCategory = data.get("seedCategory", "seeding")
        self.excludeCategories = data.get("excludeFromCopy", list())
    
    def _save(self):
        data = {
            "copy": self.copy,
            "excludeFromCopy": self.excludeCategories,
            "seedCategory": self.seedCategory,
            "repPath": str(self.repPath),
            "dstPath": str(self.dstPath),
            "clamCheck": str(self.clamUpdated)
        }

        with open(self.file, 'w') as f:
            f.write(json.dumps(data, indent=4))
        