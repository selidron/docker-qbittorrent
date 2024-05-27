import datetime
import subprocess

from Config import Config

def update(config: Config = None):
    """
    Initiate ClamAV Database update check
    """
    # Load config if not provided
    if not config:
        config = Config()
        config._load()
    
    # Check last update
    if config.clamUpdated.date() < datetime.date.today():
        subprocess.run(['freshclam'])
        config.update_clam()
    return

def scan(path):
    """
    Initiate scan of file(s) at the given path
    """
    process_args=['/usr/bin/clamscan', '-r', '--remove', path]
    process = subprocess.Popen(process_args, stdout=subprocess.PIPE)
    stdout, stderr = process.communicate()
    process.wait()

    lines = stdout.splitlines()
    for line in lines: print(str(line, 'utf-8'))
    if process.returncode == 0:
        return True
    else:
        raise RuntimeError(
            f'Clamscan returned none 0 return code: {process.returncode}\n'
            f'Stderr: {stderr.splitlines()}'
            )