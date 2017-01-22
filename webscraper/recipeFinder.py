try:
    import urllib.request as urllib2
except ImportError:
    import urllib2
from bs4 import BeautifulSoup
import pdb

def getUrls():
    url = "http://allrecipes.com";
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
    completeUrls = [url + urlSuffix for urlSuffix in urlSuffixes if urlSuffix[:7] == "/recipe"]
    return completeUrls
