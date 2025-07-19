import re
import logging
import time
from datetime import datetime, timedelta

import requests
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)


# TOI_URLS = [
#     "https://timesofindia.indiatimes.com/city/nagpur/woman-murdered-twokin-injured-in-badnera/articleshow/122528988.cms",
#     "https://timesofindia.indiatimes.com/city/patna/bihar-shocker-bjp-leader-surendra-kewat-shot-dead-in-sheikhpura-just-week-after-bizman-gopal-khemkas-murder/articleshow/122415398.cms",
#     "https://timesofindia.indiatimes.com/world/rest-of-world/partners-in-crime-how-russia-ukraine-syndicates-are-running-drug-trafficking-rackets-from-bali-with-crypto-and-encrypted-chats/articleshow/122640730.cms",
#     "http://timesofindia.indiatimes.com/city/bareilly/dalit-girl-gang-rapedin-moradabad-2-held/articleshow/122520875.cms"
# ]

# HINDU_URLS = [
#     "https://www.thehindu.com/opinion/editorial/safe-havens-no-more-on-growing-crime-against-women/article69819374.ece",
#     "https://www.thehindu.com/news/national/kerala/woman-arrested-for-assaulting-niece-pushing-police-officer-in-keralas-kannur/article69716656.ece",
#     "https://www.thehindu.com/news/national/karnataka/woman-railway-employee-assaulted-harassed-for-refusing-marriage-proposal-of-male-colleague-in-bengaluru/article69714117.ece",
#     "https://www.thehindu.com/news/national/kerala/kannur-varsity-professor-held-on-charge-of-raping-student/article69714389.ece"
# ]


def fetch_toi(url):
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        r = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(r.text, "html.parser")
        title = ""
        h1 = soup.find("h1")
        if h1:
            title = h1.get_text(strip=True)
        else:
            title_tag = soup.find("title")
            if title_tag:
                title = title_tag.get_text(strip=True)
        content = ""
        abody = soup.find("div", {"data-articlebody": "1"})
        if abody:
            ps = abody.find_all("div")
            content = "\n".join(
                [p.get_text(strip=True) for p in ps if p.get_text(strip=True)]
            )
        pub_date = ""
        for span in soup.find_all("span"):
            txt = span.get_text(strip=True)
            if re.match(r"[A-Za-z]{3} \d{1,2}, \d{4}, \d{2}:\d{2} IST", txt):
                try:
                    pub_dt = datetime.strptime(txt, "%b %d, %Y, %H:%M IST")
                    pub_date = pub_dt.strftime("%Y-%m-%dT%H:%M:%S")
                except Exception:
                    pass
                break
        return {
            "title": title,
            "content": content,
            "publication_date": pub_date,
            "url": url,
            "source": "Times of India",
        }
    except Exception:
        logger.error(f"TOI Scrape Error for {url}")
        return None

keys = ["abduction", "abuse", "accused", "acid", "alleged", "arrest", "arrested",
        "assault", "attack", "banned", "beaten", "booked", "bribery", "burglary",
        "burn", "charge", "cheat", "crime", "custody", "dead", "detain", "escape",
        "evetease", "extortion", "flee", "forgery", "fraud", "gang", "harass",
        "held", "homicide", "hostage", "illegal", "injured", "intimidat", 
        "investigat", "jail", "kidnap", "kill", "loot", "lynch", "mischief",
        "missing", "mob", "molest", "murder", "nuisance", "pedophil", "probe",
        "punish", "rape", "rape case", "robbery", "scam", "seized", "shot",
        "smuggl", "snatch", "stabbing", "stab", "suicide", "suspect", "terror",
        "theft", "threat", "torture", "vandal", "victim", "violence", "wanted"]

def fetch_48_toi(list_url="https://timesofindia.indiatimes.com/india"):
    headers = {"User-Agent": "Mozilla/5.0"}
    seen = set()
    out = []
    now = datetime.now()
    for page_num in range(1, 6):
        current_url = f"{list_url}/{page_num}"
        r = requests.get(current_url, headers=headers, timeout=15)
        soup = BeautifulSoup(r.text, "html.parser")
        # classic layout
        for li in soup.find_all("li"):
            span = li.find("span", class_="w_tle")
            if span:
                a = span.find("a", href=True)
                if a and "articleshow" in a['href']:
                    href = a['href']
                    if not href.startswith("http"):
                        href = "https://timesofindia.indiatimes.com" + href
                    if href in seen:
                        continue
                    seen.add(href)
                    art = fetch_toi(href)
                    if not art or not art.get("title") or not art.get("content"):
                        continue
                    if not any(k in art["title"].lower() for k in keys):
                        continue
                    pubdt = art.get("publication_date")
                    if pubdt:
                        pub_time = datetime.strptime(pubdt[:19], "%Y-%m-%dT%H:%M:%S")
                        diff = now - pub_time
                        if diff < timedelta(0) or diff > timedelta(hours=48):
                            continue
                    else:
                        continue
                    print(f"Added : {art['title']}")
                    out.append(art)
                    time.sleep(0.5)
        # modern layout
        for horiz in soup.find_all("div", class_=lambda c: c and c.startswith("horizontal_4")):
            for inbloc in horiz.find_all("div", class_="iN5CR"):
                a = inbloc.find("a", href=True)
                if a and "articleshow" in a['href']:
                    href = a['href']
                    if not href.startswith("http"):
                        href = "https://timesofindia.indiatimes.com" + href
                    if href in seen:
                        continue
                    seen.add(href)
                    art = fetch_toi(href)
                    if not art or not art.get("title") or not art.get("content"):
                        continue
                    if not any(k in art["title"].lower() for k in keys):
                        continue
                    pubdt = art.get("publication_date")
                    if pubdt:
                        pub_time = datetime.strptime(pubdt[:19], "%Y-%m-%dT%H:%M:%S")
                        diff = now - pub_time
                        if diff < timedelta(0) or diff > timedelta(hours=48):
                            continue
                    else:
                        continue
                    print(f"Added {art['title']}")
                    out.append(art)
                    time.sleep(0.5)
    return out

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

def fetch_48_hindu():
    base = "https://www.thehindu.com/news/national/"
    articles = []
    seen = set()
    now = datetime.now()
    for page in range(1, 6):
        url = base if page == 1 else f"{base}?page={page}"
        r = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=10)
        soup = BeautifulSoup(r.text, "html.parser")
        for ele in soup.find_all("div", class_="element row-element"):
            h3 = ele.find("h3", class_=lambda c: c and "title big" in c)
            if not h3:
                continue
            a = h3.find("a", href=True)
            if not a:
                continue
            link = a['href']
            if link in seen:
                continue
            title = a.get_text(strip=True)
            if not any(k in title.lower() for k in keys):
                continue
            seen.add(link)
            try:
                art = fetch_hindu(link)
                if not art or not art.get("publication_date"):
                    continue
                pub = art['publication_date']
                pub_dt = datetime.strptime(pub[:19], "%Y-%m-%dT%H:%M:%S")
                if timedelta(0) <= (now - pub_dt) <= timedelta(hours=48):
                    articles.append(art)
                    print(f"Added : {art['title']}")
            except Exception:
                continue
            time.sleep(0.5)
    return articles


def get_articles():
    articles = []
    articles += fetch_48_toi()
    articles += fetch_48_hindu()
    seen = set()
    unique = []
    for art in articles:
        if art and art['title'] not in seen:
            seen.add(art['title'])
            unique.append(art)
    return unique

# print(len(fetch_48_toi()))
# print(len(fetch_48_hindu()))
# print(len(get_articles()))