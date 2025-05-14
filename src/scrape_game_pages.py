from bs4 import BeautifulSoup
import json
import os
import re
from selenium import webdriver
from tqdm import tqdm
from typing import Any, Dict, List
import urllib3

from constants import DATA_DIR

applist_fh = os.path.join(DATA_DIR, "applist.json")
with open(applist_fh, "r") as f:
    applist = json.loads(f.read())

checkpoint_fh = os.path.join(DATA_DIR, "gamedetails_chkpt.json")
def save_checkpoint(gamedetails: List[Dict[str, Any]], idx: int) -> None:
    with open(checkpoint_fh, "w") as f:
        f.write(json.dumps({"gamedetails": gamedetails, "idx": idx}))
    print(f"Saving checkpoint {idx} to {checkpoint_fh}; {len(gamedetails)=}")

def load_checkpoint() -> tuple[List[Dict[str, Any]], int]:
    with open(checkpoint_fh, "r") as f:
        data = json.loads(f.read())
    idx = data["idx"]
    print(f"Loaded checkpoint {idx} from {checkpoint_fh}")
    return data["gamedetails"], idx

def load_html(appid: int) -> BeautifulSoup:
    url = f"https://store.steampowered.com/app/{appid}"

    options = webdriver.ChromeOptions()
    options.add_argument("--log-level=3")
    options.add_argument("--ignore-certificate-errors")
    options.add_argument("--incognito")
    options.add_argument("--headless")

    driver = webdriver.Chrome(options)
    driver.get(url)
    page_source = driver.page_source
    driver.close()
    return BeautifulSoup(page_source, "lxml")

def parse_page(soup: BeautifulSoup) -> Dict[str, Any]:
    page_data = {"appid": appid}

    # reviews
    pattern = re.compile(r"\((\d+)% of ([\d,]+)\)")
    for review_desc in soup.find_all(class_="responsive_reviewdesc_short"):
        match_ = pattern.search(review_desc.text)
        if match_ is None:
            continue
        positive_review_pct, num_reviews = match_.groups()
        positive_review_pct = int(positive_review_pct)
        num_reviews = int(num_reviews.replace(",", ""))
        if review_desc.span.text == "All Time":
            page_data["all_positive_review_pct"] = positive_review_pct
            page_data["total_num_reviews"] = num_reviews
        elif review_desc.span.text == "Recent":
            page_data["recent_positive_review_pct"] = positive_review_pct
            page_data["recent_num_reviews"] = num_reviews

    # short description
    description = soup.find(class_="game_description_snippet")
    if description is not None:
        page_data["description_snippet"] = description.text.strip()

    # publisher / developer
    for dev_row in soup.find_all(class_="dev_row"):
        subtitle = dev_row.find(class_="subtitle column")
        if subtitle is None:
            continue
        row_type = subtitle.text.strip()
        names = list({x.text.strip() for x in dev_row.find_all("a")})
        if row_type == "Developer:":
            page_data["developers"] = names
        elif row_type == "Publisher:":
            page_data["publishers"] = names


    # release date
    release_date = soup.find(class_="release_date")
    if release_date:
        page_data["release_date"] = (
            release_date.find(class_="date").text.strip()
        )

    # popular tags
    page_data["tags"] = list({
        x.text.strip() for x in soup.find_all(class_="app_tag")
    })

    # price
    # NOTE omitting bundles and sales to keep things a bit simpler
    for purchase_action in soup.find_all(class_="game_purchase_action_bg"):
        price = None
        discount = purchase_action.find_all(class_="discount_original_price")
        if discount:
            price = discount[0]
        else:
            price = purchase_action.find(class_="game_purchase_price price")
        if price:
            price = price.text.strip()
            if price == "Free To Play":
                page_data["price"] = 0
            else:
                match_ = re.search("(\d+\.\d{2})", price)
                if match_ is None:
                    continue
                page_data["price"] = float(match_.groups()[0])
            break

    # features
    page_data["features"] = list({
        x.text.strip()
        for x in soup.find_all("a", class_="game_area_details_specs_ctn")
    })

    # long description
    description = soup.find(class_="game_area_description")
    if description:
        page_data["description"] = description.text.strip()

    return page_data

if os.path.exists(checkpoint_fh):
    gamedetails, starting_idx = load_checkpoint()
else:
    gamedetails = []
    starting_idx = 0

for idx in tqdm(range(starting_idx, len(applist))):
    if idx and idx % 100 == 0:
        save_checkpoint(gamedetails, idx + 1)
    try:
        appid = applist[idx]["appid"]
    except Exception as e:
        continue
    if int(appid) in (440810,):
        continue

    max_tries = 3
    for try_count in range(max_tries):
        try:
            soup = load_html(appid)
        except urllib3.exceptions.ReadTimeoutError as e:
            if try_count == max_tries - 1:
                print(f"retries exceeded on {idx=} {appid=}")
                save_checkpoint(gamedetails, idx)
                raise
            else:
                print(f"retry count on {idx=} {appid=}: {try_count}")
        except:
            print(f"error on {idx=} {appid=}")
            save_checkpoint(gamedetails, idx)
            raise
        else:
            break

    # some of the urls will resolve to the steam home page
    if soup.find_all(class_="home_page_col_wrapper"):
        continue
    page_data = parse_page(soup)
    gamedetails.append(page_data)

with open(os.path.join(DATA_DIR, "gamedetails.json"), "w") as f:
    f.write(json.dumps(gamedetails))
