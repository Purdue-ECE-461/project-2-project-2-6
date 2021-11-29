from git import Repo, RemoteProgress, exc

import os
from tqdm import tqdm
import logging
import stat


log = logging.getLogger(__name__)

# from https://stackoverflow.com/questions/51045540/python-progress-bar-for-git-clone
class CloneProgress(RemoteProgress):
  def __init__(self):
      super().__init__()
      self.pbar = tqdm()

  def update(self, op_code, cur_count, max_count=None, message=''):
      self.pbar.total = max_count
      self.pbar.n = cur_count
      self.pbar.refresh()

def get_clone(url, dest = "./repo"):
  if not os.path.isdir(dest):
    os.mkdir(dest)
  try:
    Repo.clone_from(url, dest)
    log.info("Clone successful")
  except exc.GitCommandError:
    log.debug("File already cloned or .git file already in " + dest)
    return 0
  except:
    log.debug("Failed to clone.")
    return 0
  return 1

def rm_clone(top = "./repo"):
  rmtree(top)
  log.info("repo folder is cleaned.")
  return 1

def rmtree(top):
    for root, dirs, files in os.walk(top, topdown=False):
        for name in files:
            filename = os.path.join(root, name)
            os.chmod(filename, stat.S_IWUSR)
            os.remove(filename)
        for name in dirs:
            os.rmdir(os.path.join(root, name))
    os.rmdir(top)