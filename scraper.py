import json
import logging
import time
from datetime import datetime

import requests
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)

TOI_URLS = [
    "https://timesofindia.indiatimes.com/city/nagpur/woman-murdered-twokin-injured-in-badnera/articleshow/122528988.cms",
    "https://timesofindia.indiatimes.com/city/patna/bihar-shocker-bjp-leader-surendra-kewat-shot-dead-in-sheikhpura-just-week-after-bizman-gopal-khemkas-murder/articleshow/122415398.cms",
    "https://timesofindia.indiatimes.com/world/rest-of-world/partners-in-crime-how-russia-ukraine-syndicates-are-running-drug-trafficking-rackets-from-bali-with-crypto-and-encrypted-chats/articleshow/122640730.cms",
    "http://timesofindia.indiatimes.com/city/bareilly/dalit-girl-gang-rapedin-moradabad-2-held/articleshow/122520875.cms"
]

HINDU_URLS = [
    "https://www.thehindu.com/opinion/editorial/safe-havens-no-more-on-growing-crime-against-women/article69819374.ece",
    "https://www.thehindu.com/news/national/kerala/woman-arrested-for-assaulting-niece-pushing-police-officer-in-keralas-kannur/article69716656.ece",
    "https://www.thehindu.com/news/national/karnataka/woman-railway-employee-assaulted-harassed-for-refusing-marriage-proposal-of-male-colleague-in-bengaluru/article69714117.ece",
    "https://www.thehindu.com/news/national/kerala/kannur-varsity-professor-held-on-charge-of-raping-student/article69714389.ece"
]


def fetch_toi(url):
    try:
        headers = {
            "User-Agent": "Mozilla/5.0"
        }
        r = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(r.text, "html.parser")
        title = (soup.find("h1") or soup.find("title")).get_text(strip=True)
        body = ''
        # Try to extract articleBody from JSON in scripts
        for sc in soup.find_all('script'):
            if sc.string and 'articleBody' in sc.string:
                try:
                    json_data = json.loads(sc.string)
                    body = json_data.get("articleBody", "")
                    break
                except Exception:
                    continue
        meta = soup.find('meta', attrs={'property':'article:published_time'}) or soup.find('meta', attrs={'property':'og:updated_time'})
        pub_date = meta['content'] if meta and meta.has_attr('content') else ""
        return {
            "title": title,
            "content": body.strip(),
            "publication_date": pub_date,
            "url": url,
            "source": "Times of India"
        }
    except Exception as err:
        logger.error(f"TOI scrape error for {url}: {err}")
        return None

def fetch_hindu(url):
    try:
        headers = {
            "User-Agent": "Mozilla/5.0"
        }
        r = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(r.text, "html.parser")
        title_elem = soup.find("h1", class_="title")
        title = title_elem.get_text(strip=True) if title_elem else ""
        date_meta = soup.find("meta", itemprop="datePublished")
        pub_date = date_meta["content"] if date_meta and date_meta.has_attr("content") else ""
        content_div = None
        for div in soup.find_all("div", class_="articlebodycontent"):
            if div.has_attr("id") and div["id"].startswith("content-body-"):
                content_div = div
                break
        content = ""
        if content_div:
            paragraphs = content_div.find_all("p")
            content = "\n".join(p.get_text(strip=True) for p in paragraphs if p.get_text(strip=True))
        return {
            "title": title,
            "publication_date": pub_date,
            "content": content,
            "url": url,
            "source": "The Hindu"
        }
    except Exception as exc:
        logger.error(f"Hindu Scrape Error for {url}: {exc}")
        return None

def get_articles():
    articles = []
    for url in TOI_URLS:
        a = fetch_toi(url)
        articles.append(a)
        time.sleep(1)
    for url in HINDU_URLS:
        a = fetch_hindu(url)
        articles.append(a)
        time.sleep(1)
    # Remove duplicate titles
    seen = set()
    unique = []
    for art in articles:
        if art['title'] not in seen:
            seen.add(art['title'])
            unique.append(art)
    return unique
