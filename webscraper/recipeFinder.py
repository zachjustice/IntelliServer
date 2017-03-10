try:
    import urllib.request as urllib2
except ImportError:
    import urllib2
from bs4 import BeautifulSoup
import pdb
from selenium import webdriver

def getUrls():
    categories = [('78/breakfast-and-brunch/', ['breakfast']), ('17561/lunch/', ['lunch']), ('17562/dinner/', ['dinner']), ('80/main-dish/', ['lunch', 'dinner'])]
    numPages = 1000 #try max pages from each category
    allUrls = getCategoryUrls(categories, numPages)
    return allUrls


def getCategoryUrls(categories, numPages):
    allUrls = []
    for categoryBase in categories:
        s = set()
        for i in range(numPages):
            toAdd = getPage(categoryBase[0], i)
            if toAdd is None:
                break
            else:
                [s.add(url) for url in toAdd]
        allUrls.append((categoryBase[1], s))
    return allUrls

def getPage(categoryBase, page):
    base = "http://allrecipes.com/recipes/"
    url = base + categoryBase + "?page=" + str(page) + str("#0");
    print(str(url))
    try:
        page = urllib2.urlopen(url).read();
    except Exception as e:
        print(e)
        return None
    soup = BeautifulSoup(page, "html.parser");

    urlSuffixes = [];

    body_content = soup.find("div", {"class": "container-content body-content"});
    grid = body_content.find("section", {"id": "grid"});
    for article in grid.findAll("article", {"class": "grid-col--fixed-tiles"}):
        link = None
        links = article.findAll("a")
        if len(links) > 1:
            link = links[1]
        if link is not None:
            urlSuffixes.append(link.get("href"));
    recipeBase = "http://allrecipes.com"
    completeUrls = [recipeBase + urlSuffix for urlSuffix in urlSuffixes if urlSuffix[:7] == "/recipe"]
    return completeUrls
