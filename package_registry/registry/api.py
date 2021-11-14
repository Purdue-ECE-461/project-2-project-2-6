import re
from django.db.utils import Error
import requests
import logging

from bs4 import BeautifulSoup
from github import Github
from metrics import *
from os import environ
from utils import readURLs, splitBaseURL_repo, unzipEncoded, parseJson
from soupsieve.util import lower

log = logging.getLogger(__name__)

token = environ.get('GITHUB_TOKEN')#'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'
g = Github(token)

class PackageParser():
    def __init__(self, zip):
        unzipEncoded(zip)
        self.data = parseJson()
        self.url = data["repository"]["url"]
        stringBroken = splitBaseURL_repo(self.url) #stringBroken[0] = baseURL ; stringBroken[1] = repoName
        self.repoName = stringBroken[1]

    def rate(self):
        #Do computation using the above values.!
        users = self.getUsers()
        self.contributor_score, contributors_count = self.getContributors(users) # bus_factor

        self.respon_score = self.getResponsivenessScore(contributors_count, users)
        self.correc_score = get_correctness(self.repoName)
        self.ramp_up_score = get_ramp_up_time(self.url, self.repoName)
        self.li_score = self.getLicenseScore()
        self.pinned_dep_score = get_pinned_dep_ratio(self.data["dependencies"])
        # net_score = 0.1*ramp_up_score + 0.2*correc_score + 0.25*contributor_score + 0.15*respon_score + 0.3*li_score 
        
        self.scores = [self.pinned_dep_score, self.ramp_up_score, self.correc_score, self.contributor_score, self.respon_score, self.li_score]

        for score in self.scores:
            if score < 0.5:
                raise ValueError
                
    def getLicenseScore (self):
        #we have decided we dont care if a repo has licenses or not, we are only gonna grade it if they have a license.txt under which all the licenses should be mentioned.
        #if a repo has mentioned some xyz licenses under its read me section or inside its code that is going to be ignored.
        assignedScope = 0

        # Using this link http://www.gnu.org/licenses/gpl-faq.html#AllCompatibility we determine that LGPLv2.1 are compatable with everything to the left of it in the link.. using that info and other link mentioend below
        preDefinedListOfAcceptedLicenses = ["MIT License","X11 License","Apache","MIT","X11", "Apache version 2.0 license", "BSD", "Public Domain"] # https://dwheeler.com/essays/floss-license-slide.html this article and some research was used to determine the list of accepted license. https://www.gnu.org/licenses/old-licenses/lgpl-2.1.html Used this as wel.
        license = 0
        listOfLicensesFound = []

        repo = g.get_repo(self.repoName)

        #get_licenses is giving error..therefore have a try catch block.
        try:
            license  = repo.get_license()
        except:
            return assignedScope #returning as no licenses found.!

        #if we are here we have a licenes now we can get list of licesnses and compare.
        licenses = license.license

        #sometimes there could be a list of licenses other time we can get just one license..so having a try catch as was getting a error license is not iterable.
        try:
            for items in licenses: #looping through all licesnses
                nameOfLicense = items.name
                listOfLicensesFound.add(nameOfLicense)   
        except:
            nameOfLicense = licenses.name
            listOfLicensesFound.append(nameOfLicense)  

        #when here irrespective of one license or multiple license...I have a list of all licenses.
        notfoundinLoop = 0
        for namesFound in listOfLicensesFound:
            notfoundinLoop = 0
            namesFound = namesFound.lower()
            #parse through the known license to see if matches.!
            for names in preDefinedListOfAcceptedLicenses:
                names = names.lower()
                if (namesFound == names):
                    assignedScope = assignedScope+1
                    notfoundinLoop = 0
                    break
                else:
                    notfoundinLoop = 1

            if (notfoundinLoop == 1):     
                #added this here I do understand this is incorrect as this will make the score to 1.25 However it doesnt matter as check already present below and score of 1 is already assigned a point 1.
                assignedScope = assignedScope + 0.25#assigned 0.25 for other license not in list I know, my list of license would not be too extensive, also different languages and all so accounting for it.
        
        # here we have the scope. accounting that some reop might have many license.!
        if (assignedScope == 0):
            return 0
        elif ((assignedScope > 0.0) and (assignedScope <= 0.25)) :
            return 0.25
        elif ((assignedScope > 0.25) and (assignedScope < 1)) :
            return 0.75
        else :
            return 1
            
        #done final score for licenses will be returned.!   


    def getResponsivenessScore (self, contributors_count, users):
        #https://github.com/pullreminders/backlog/issues/53 Used this link for ideas.!
        assignedScope = 0

        repo = g.get_repo(self.repoName)
        closedIssues = repo.get_issues(state='closed')
        totalCountOFClosedIssues = closedIssues.totalCount #number of closed issue tell us how much responsive the repo is.!

        #Assigning score based on output.!
        if (totalCountOFClosedIssues <= 200):
            assignedScope = 0.25
        elif ((totalCountOFClosedIssues <= 600) and (totalCountOFClosedIssues > 200)) :
            assignedScope = 0.50 
        elif ((totalCountOFClosedIssues <= 1000) and (totalCountOFClosedIssues > 600)) :
            assignedScope = 0.75 
        else:
            assignedScope = 1 


        #second factor (average of number of users who comments, pulls and reviewed the code)
        numComments = repo.get_comments().totalCount
        numPulls = repo.get_pulls().totalCount
        numReviews = repo.get_watchers().totalCount

        factor2Avg = ((numComments + numPulls + numReviews) / 3)

        #Assigning score based on output.!
        if (factor2Avg <= 150):
            assignedScope = assignedScope + 0.25
        elif ((factor2Avg <= 800) and (factor2Avg > 150)) :
            assignedScope = assignedScope + 0.50 
        elif ((factor2Avg <= 800) and (factor2Avg > 4000)) :
            assignedScope = assignedScope + 0.75 
        else:
            assignedScope = assignedScope + 1 


        #thrid factor.! Number of users V/S Contributers will tell how much the ratio there is.!
        if (users == 0) :
            thirdFactor = 0
        else :
            thirdFactor = (contributors_count / users) * 1000

        if (thirdFactor == 0):
            assignedScope = assignedScope + 0.0
        elif (thirdFactor <= 0.02):
            assignedScope = assignedScope + 0.25
        elif ((thirdFactor <= 0.05)):
            assignedScope = assignedScope + 0.50 
        elif ((thirdFactor <= 0.09)):
            assignedScope = assignedScope + 0.75 
        else:
            assignedScope = assignedScope + 1

        assignedScope = assignedScope / 3 #because we considered 3 factors.
        return assignedScope

    def getUsers(self):
        page = requests.get(self.url)
        soup = BeautifulSoup(page.content, 'html.parser')
        newList = soup.find_all('h2')
        count = 0
        users = 0 #set default number of users

        for points in newList:
            count += 1
            point = str(points.text)
            if "used by" in lower(point):
                newString = re.findall('"([^"]*)"', str(newList[count - 1]).partition("title=")[2].replace(',', ''))
                users = int(newString[0])

        try:
            repo = g.get_repo(self.repoName)
            user_count = repo.get_contributors(anon=True).totalCount
        except:
            user_count = 0

        return max(users, user_count)

    def getContributors(self, users):
        try:
            repo = g.get_repo(self.repoName)
            contributors_count = repo.get_contributors(anon=True).totalCount
        except:
            contributors_count = int(max(1, .00002 * users))

        if contributors_count < 10:
            return 0.0, contributors_count
        elif contributors_count < 50:
            return .25, contributors_count
        elif contributors_count < 100:
            return .5, contributors_count
        elif contributors_count < 200:
            return .75, contributors_count
        else:
            return 1.0, contributors_count

    def __str__(self):
        for ele in self.scores:
            print("{0} {1:.2f} {2:.2f} {3:.2f} {4:.2f} {5:.2f} {6:.2f}".format(*ele, sep=" "))
    

if __name__=="__main__":
    urls = readURLs("Url.txt")
    print(PackageParser(urls[0]).rate())
