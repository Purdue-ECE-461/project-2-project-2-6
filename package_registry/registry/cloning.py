from git import Repo, RemoteProgress, exc
import os
import string
from tqdm import tqdm
import logging
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

def get_clone(url):
  if not os.path.isdir("./repo"):
    os.system("mkdir ./repo")
  try:
    Repo.clone_from(url, "./repos", branch='master', progress=CloneProgress())
    log.info("Clone successful")
  except exc.GitCommandError:
    log.debug("File already cloned or .git file already in ./repo")
    return 0
  except:
    log.debug("Failed to clone.")
    return 0
  return 1

def rm_clone():
  os.system("rm -rf ./repo/")
  log.info("repo folder is cleaned.")
  return 1