from bs4 import BeautifulSoup
import base64
import json
import os
import requests
import zipfile
import shutil


def parseJson(file = "./repo"):
    file = find("package.json", file)
    if file is None:
        return None
    f = open(file)
    return json.load(f)    

def unzipEncoded(encoded, out = "./repo"):
    with open('output_file.zip', 'wb') as result:
        result.write(base64.b64decode(encoded))
    with zipfile.ZipFile('output_file.zip', 'r') as zip_ref:
        zip_ref.extractall(out)
    os.remove('output_file.zip')

def zip_and_encode(zip_dir = "./repo", out = "test"):
    shutil.make_archive(out, "zip", zip_dir)
    encoded = encode(out + ".zip")
    if os.path.exists(out + ".zip"):
        os.remove(out + ".zip")
    return str(encoded)[2:-1]

def encode(path):
    with open(path, "rb") as result:
        return base64.b64encode(result.read())

def readURLs(filename, isTesting = False):
    #opening file and doing operations on file.
    file = open(filename, 'r')
    lines = file.readlines() #lines will be a list of all lines in file. meaning list of urls.

    urls = []
    for line in lines:
        url = line.strip() #this is done as helps in debugging as URL can be seen directly.
        if "https://www.npmjs" in url:
            url = fixUrl(url)
        urls.append(url)
    file.close()

    return urls

def sortPackages(packages):
    packages.sort(key=lambda x:x.scores[0], reverse=True) # sort descending

def splitBaseURL_repo(url):
    # doing string manuplation to break into repo and base url.
    chartoSplitFrom = "/"
    occurrence = 3

    val = -1
    for i in range(0, occurrence):
        val = url.find(chartoSplitFrom, val + 1)

    baseURL = url[0:val]
    repoName = url[val+1:len(url)]

    #returns baseURL and repoName.!
    return baseURL,repoName

def fixUrl(url):
    point = url
    page = requests.get(url)
    soup = BeautifulSoup(page.content, 'html.parser')
    for points in soup.find('a', class_="b2812e30 f2874b88 fw6 mb3 mt2 truncate black-80 f4 link"):
        point = str(points.text)
    return "https://" + point

def find(name, path):
    for root, dirs, files in os.walk(path):
        if name in files:
            return os.path.join(root, name)
    return None
    
def strip_git(s):
    if s[:6] == "git://":
        s = s[6:]
    if s[-4:] == ".git":
        s = s[:-4]
    return s