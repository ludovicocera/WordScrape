import bs4
import requests
import re
import collections
import string
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
    html = urlopen(url).read()

    soup = bs4.BeautifulSoup(html, "html.parser")

    for script in soup(["script", "style"]):
        script.extract()

    for element in soup.body.find_all(text=True):

        if isinstance(element, Comment):
            element.extract()

    wordList = soup.text.split()

    cleanedText = list()

    for word in wordList:
        cleanedText.append(word.lower().translate(
            str.maketrans('', '', string.punctuation)))

    return cleanedText


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


def tag_visible(element):
    if element.parent.name in ['style', 'script', 'head', 'title', 'meta', '[document]']:
        return False
    if isinstance(element, Comment):
        return False
    return True


def text_from_html(body):
    soup = bs4.BeautifulSoup(body, 'html.parser')
    texts = soup.findAll(text=True)
    visible_texts = filter(tag_visible, texts)
    return u" ".join(t.strip() for t in visible_texts)


visited = set()

totalWords = list()

wordsDict = {}

url = input("Enter the website you want to WordScrape: ")

visit(url)

print(visited)

for element in totalWords:
    wordsDict[element] = totalWords.count(element)

print(sorted(wordsDict.items(), key=lambda kv: kv[1], reverse=True))
