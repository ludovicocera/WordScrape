import bs4
import requests
import re
import collections
from bs4 import Comment
from urllib.parse import urlparse
from urllib.request import urlopen, URLError


def visit(url):

    if validateUrl(url):
        print("Visiting " + url)

        visited.add(url)
        totalWords.extend(scrapeWords(url))

        linkSet = collectLinks(url)

        for link in linkSet:

            if link not in visited:
                visit(link)


def scrapeWords(url):
    r = requests.get(url)

    soup = bs4.BeautifulSoup(r.text, "html.parser")

    for script in soup(["script", "style"]):
        script.extract()

    for element in soup.body.find_all(text=True):

        if isinstance(element, Comment):
            element.extract()

    cleanedText = re.sub('[^a-zA-Z0-9 ]+', ' ', soup.text.lower())

    wordList = cleanedText.split()

    return wordList


def collectLinks(url):
    r = requests.get(url)

    linkSet = set()

    if r.status_code == 200:
        soup = bs4.BeautifulSoup(r.text, "html.parser")
        domain = getDomain(url)

        try:

            for link in soup.body.find_all("a"):
                linkStr = link.get("href")

                if (linkStr is not None and linkStr != ""):

                    if linkStr[0] == "/":
                        addedDomain = domain + linkStr
                        linkSet.add(addedDomain)

                    elif (linkStr[0:4] != "http" or linkStr[0:3] != "www"):
                        addedDomain = domain + "/" + linkStr
                        linkSet.add(addedDomain)

                    elif getDomain(linkStr) == domain:
                        linkSet.add(linkStr)

        except AttributeError:
            print("Couldn't retrieve HTML body")

    return linkSet


def getDomain(link):
    parsed_uri = urlparse(link)
    result = '{uri.scheme}://{uri.netloc}'.format(uri=parsed_uri)
    return result


def validateUrl(url):

    try:
        urlopen(url)
        return True

    except URLError:
        return False


visited = set()

totalWords = list()

wordsDict = {}

url = input("Enter the website you want to WordScrape: ")

visit(url)

print(visited)

for element in totalWords:
    wordsDict[element] = totalWords.count(element)
    
print(sorted(wordsDict.items(), key=lambda kv: kv[1], reverse = True))
