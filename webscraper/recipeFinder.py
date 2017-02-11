try:
    import urllib.request as urllib2
except ImportError:
    import urllib2
from bs4 import BeautifulSoup
import pdb
def getUrls():
    allUrls = []
    s = set()
    for i in range(5):
        toAdd = getPage(i)
        allUrls.extend(toAdd)
        [s.add(url) for url in toAdd]
    print (len(allUrls))
    return s
def getPage(page):
    base = "https://allrecipes.com/"
    url = base + "?page=" + str(page);
    page = urllib2.urlopen(url).read();
    soup = BeautifulSoup(page, "html.parser");

    urlSuffixes = [];

    body_content = soup.find("div", {"class": "container-content body-content"});
    section = body_content.find("section", {"id": "ar_home_index"});
    grid = section.find("section", {"id": "grid"});
    for article in grid.findAll("article", {"class": "grid-col--fixed-tiles"}):
        link = article.find("a")
        if link is not None:
            urlSuffixes.append(link.get("href"));
    completeUrls = [base + urlSuffix for urlSuffix in urlSuffixes if urlSuffix[:7] == "/recipe"]
    return completeUrls
