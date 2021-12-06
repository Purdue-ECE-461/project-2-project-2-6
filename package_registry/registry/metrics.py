from github import Github, GithubException
import os
import re
import logging
from .utils import find


log = logging.getLogger(__name__)

token = os.environ.get("TOKEN")
g = Github(token)

def get_correctness(repos_name):
    git_repo = g.get_repo(repos_name)
    score = 0
    stars = git_repo.stargazers_count
    if (stars >= 150 and stars < 500):
        score += 0.05
    elif (stars  <= 800):
        score += 0.09
    elif (stars <= 1500):
        score += 0.16
    elif (stars <= 5000):
        score += 0.21
    elif (stars <= 12000):
        score += 0.26
    elif (stars > 12000):
        score += 0.3

    closed_issues = git_repo.get_issues(state='closed').totalCount
    if closed_issues == 0:
        score -= 0.1
    else:
        issue_ratio = git_repo.get_issues(state='open').totalCount/closed_issues
        totalIssues = git_repo.get_issues().totalCount
        if (totalIssues > 50):
            if (issue_ratio < 0.05):
                score += 0.2
            elif (issue_ratio < 0.1):
                score += 0.15
            elif (issue_ratio < 0.25):
                score += 0.05
            elif (issue_ratio > 0.5):
                score -= 0.1

    closed_pulls = git_repo.get_pulls(state='closed', sort='created').totalCount
    if closed_pulls == 0:
        score -= 0.1
    else:
        open_pulls = git_repo.get_pulls(state='open', sort='created').totalCount
        if (open_pulls/closed_pulls < 0.2): # This was suppossed to be merged comparison. But there is no direct status for that.
            score += 0.1
    try:
        try:
            branch = git_repo.get_branch("master")
        except GithubException:
            branch = git_repo.get_branch("main")
        if (branch.protected == True):
            score += 0.2
    except:
        log.info("Using non standard branch master names")
        score -= 0.1

    try:
        open_milestones = git_repo.get_milestones(state="open").totalCount
        total_milestones = git_repo.get_milestones(state="closed").totalCount + open_milestones
        if total_milestones > 5:
            if open_milestones/total_milestones <= 0.2:
                score += 0.1
    except:
        log.debug("No milestones")
        score -= 0.1

    try:
        numRelease = git_repo.get_releases().totalCount
        if (numRelease > 35):
            score += 0.3
        elif (numRelease > 20):
            score += 0.2
        elif (numRelease > 10):
            score += 0.1
    except:
        log.debug("No releases")
        score -= 0.1

    contents = git_repo.get_contents("")
    for c in contents:
        if (c.path.lower() in ["test", "tests", "testcase"]):
            score += 0.2
        if (c.path == ".gitignore"):
            score += 0.05

    if score < 0:
        score = 0
    elif score > 1:
        score = 1
    return score

def get_ramp_up_time(repos_url, repos_name):
    repo = g.get_repo(repos_name)
    contents = repo.get_contents("")
    readme_name = ""
    eslint_out = ""
    score = 0
    for c in contents:
        if ("readme" in c.path.lower()):
            score += 0.1
            readme_name = c.path
        if (".eslintrc" in c.path):
            score += 0.1
    log.debug("Working on {0}".format(repos_name))
    
    if readme_name != "":
        readme_size = os.path.getsize(find(readme_name, "./repo")) # I really wish there was a python linter for this
        if readme_size < 50:
            score -= 0.1
        elif readme_size < 1000 and readme_size > 500:
            score += 0.1
        elif readme_size < 5000:
            score += 0.2
        elif readme_size < 20000:
            score += 0.3
        elif readme_size < 45000:
            score += 0.2
        elif readme_size <= 70000:
            score += 0.1
        elif readme_size > 85000:
            score -= 0.1
    
    os.system("npx eslint ./repo --no-eslintrc --quiet > ./tmp.log")

    ret = 0
    if os.path.isfile("./tmp.log"):
        with open("./tmp.log", "r") as fptr:
            eslint_out = fptr.read()
    if ret == 0:
        re_list_eslint = re.findall(r"problems\s+\((\d+).*?\)\s*$", eslint_out)
        num_errors = int(501 if not re_list_eslint else re_list_eslint[0])
        log.info("Number of detected errors: {0}".format(num_errors))
        if num_errors < 10:
            score += 0.5
        elif num_errors < 35:
            score += 0.4
        elif num_errors < 100:
            score += 0.3
        elif num_errors < 250:
            score += 0.2
        elif num_errors < 500:
            score += 0.1

    if score < 0:
        score = 0
    elif score > 1:
        score = 1
    os.remove("./tmp.log")
    return score

    
def get_pinned_dep_ratio(data):
    if "dependencies" not in data:
        return 0
    pinned = 0
    total = 0
    pattern = re.compile(r"\d+.\d+.(\d+|X)")
    for i in data["dependencies"]:
        total += 1
        if re.match(pattern, data["dependencies"][i]) is not None:
            pinned += 1
    return 0 if total == 0 else pinned / total
    
if __name__== "__main__":
    data = {"dependencies": {"pinned": "2.6.X", "pinned_2": "0.4.3", "unpinned": "~1.2.3"}}
    print(get_pinned_dep_ratio(data))