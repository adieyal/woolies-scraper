from __future__ import print_function
import datetime
import requests
from bs4 import BeautifulSoup
import sys
import time
import unicodecsv as csv

MAXLIMIT = 20000
url = "http://www.woolworths.co.za/store/cat/Food/_/N-1z13sk4?No={start_index}&Nr=NOT%28isSkuActive%3A0%29&Nrpp=1000"

def exstr(tag):
    if tag:
        return tag.text.strip()
    return None

def extract(soup):
    data = []
    products = soup.findAll(attrs={"itemtype" : "http://schema.org/Product"})
    for product in products:
        name = exstr(product.find(attrs={"itemprop" : "name"}))
        price = exstr(product.find(attrs={"itemprop" : "price", "class" : "price"}))
        buy_save = exstr(product.find(attrs={"itemprop" : "price", "class" : "buySavePrice"}))
        image = product.find(attrs={"itemprop" : "image"})["src"]
        sku = product.find(attrs={"class" : "shoppingListCommerceWrapper"})["id"]
        data.append([name, price, buy_save, sku, datetime.datetime.now()])
    return data

def clean(soup):
    def remove_all(tags):
        [a.extract() for a in tags]
    remove_all(soup.select("#qtyContainer"))
    remove_all(soup.select("script"))
    remove_all(soup.select("link"))
    remove_all(soup.select("meta"))
    remove_all(soup.select(".headerNavWrapper"))
    remove_all(soup.select("head"))
    remove_all(soup.select(".siteNav"))
    remove_all(soup.select(".siteHeader"))
    remove_all(soup.select("nav"))
    remove_all(soup.select(".userDetails"))
    remove_all(soup.select("#cartDetails"))
    remove_all(soup.select(".subMenu"))
    remove_all(soup.select(".hoverDetails"))
    remove_all(soup.select(".productColours"))
    remove_all(soup.select(".qtyBasket"))
    remove_all(soup.select(".addLists"))
    remove_all(soup.select("style"))

    with open("out.html", "w") as fp:
        fp.write(unicode(soup.prettify()).encode("utf8"))

if __name__ == "__main__":
    with open("prices_all.csv", "a") as fp:
        writer = csv.writer(fp)
        count = 1
        while True:
            try:
                new_url = url.format(start_index=count)
                print(new_url)
                html = requests.get(new_url, timeout=25).content
                soup = BeautifulSoup(html, "html.parser")
                data = extract(soup)
                writer.writerows(data)
                if len(data) < 1000:
                    break
                count += 1000
                if count > MAXLIMIT: break
            except requests.exceptions.Timeout:
                time.sleep(10)

