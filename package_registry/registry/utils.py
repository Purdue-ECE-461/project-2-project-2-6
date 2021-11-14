import requests
import zipfile
import json
import base64
import os

from bs4 import BeautifulSoup

def parseJson(file = "./repo/package.json"):
    f = open(file)
    return json.load(f)

def unzipEncoded(encoded):
    with open('output_file.zip', 'wb') as result:
        result.write(base64.b64decode(encoded))
    with zipfile.ZipFile('output_file.zip', 'r') as zip_ref:
        zip_ref.extractall("./repo")
    os.remove('output_file.zip')

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

def unzip(file):
    with zipfile.ZipFile(file, 'r') as zip_ref:
        zip_ref.extract("package.json")

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
    