from datetime import datetime
import json
import os
from tqdm import tqdm

from constants import DATA_DIR
from database import (
    Author,
    Company,
    create_all,
    Developer,
    Game,
    GameFeature,
    GameTag,
    GameTagEnumeration,
    get_session,
    FeatureEnumeration,
    Feedlabel,
    Feedname,
    Newsitem,
    NewsitemTagEnumeration,
    NewsitemTags,
    Publisher,
)

applist_fh = os.path.join(DATA_DIR, "applist.json")
with open(applist_fh, "r") as f:
    applist = json.loads(f.read())

newsitems_fh = os.path.join(DATA_DIR, "newsitems.json")
with open(newsitems_fh, "r") as f:
    newsitems = json.loads(f.read())

gamedetails_fh = os.path.join(DATA_DIR, "gamedetails.json")
with open(gamedetails_fh, "r") as f:
    gamedetails = json.loads(f.read())

final_ids = (
    {x["appid"] for x in applist} &
    {x["appid"] for x in gamedetails}
)

print("creating tables")
create_all()

print("getting session")
SESSION = get_session()

# add the name from applist to gamedetails
details = {}
for app in applist:
    appid = app["appid"]
    if appid in final_ids:
        details[appid] = app

# developers, publishers, tags, and features should be pulled out of gamedetails into separate dataframes
developers = set()
publishers = set()
company_map = {}
tag_map = {}
feature_map = {}
# accidentally created some duplicate entries
seen_appids = set()
print("parsing gamedetails")
for game in tqdm(gamedetails):
    appid = game["appid"]
    if not appid in final_ids or appid in seen_appids:
        continue
    seen_appids.add(appid)
    release_date = game.get("release_date", "").strip()
    game["coming_soon"] = False
    if release_date == "Coming soon":
        game["coming_soon"] = True
        release_date = None
    else:
        try:
            release_date = datetime.strptime(game["release_date"], "%b %d, %Y")
        except Exception as e:
            # this can take on values like "To be announced" or "Q2 2025"
            # I don't really feel like dealing with that nuance at this time
            release_date = None
    game["release_date"] = release_date
    items_to_add = []
    for company in game.pop("developers", []):
        company = company.strip()
        if company in company_map:
            company_id = company_map[company]
        else:
            company_id = len(company_map) + 1
            company_map[company] = company_id
            SESSION.add(Company(
                company_id=company_id,
                company=company,
                is_developer=False,
                is_publisher=False,
            ))
        developers.add(company_id)
        items_to_add.append(Developer(
            company_id=company_id,
            # developer_id=developer_id,
            appid=appid,
        ))
    for company in game.pop("publishers", []):
        company = company.strip()
        if company in company_map:
            company_id = company_map[company]
        else:
            company_id = len(company_map) + 1
            company_map[company] = company_id
            SESSION.add(Company(
                company_id=company_id,
                company=company,
                is_developer=False,
                is_publisher=False,
            ))
        publishers.add(company_id)
        items_to_add.append(Publisher(
            company_id=company_id,
            # publisher_id=publisher_id,
            appid=appid,
        ))
    for tag in game.pop("tags", []):
        tag = tag.strip()
        # the steam page for games has a "+" button to add tags; I should have
        # filtered it out in the web scraping, but I will do it here since I
        # missed it before
        if tag == "+":
            continue
        if tag in tag_map:
            tag_id = tag_map[tag]
        else:
            tag_id = len(tag_map) + 1
            tag_map[tag] = tag_id
            SESSION.add(GameTagEnumeration(
                game_tag_enumeration_id=tag_id,
                tag=tag,
            ))
        items_to_add.append(GameTag(
            appid=appid,
            game_tag_enumeration_id=tag_id,
        ))
    for feature in game.pop("features", []):
        feature = feature.strip()
        if feature in feature_map:
            feature_id = feature_map[feature]
        else:
            feature_id = len(feature_map) + 1
            feature_map[feature] = feature_id
            SESSION.add(FeatureEnumeration(
                feature_enumeration_id=feature_id,
                feature=feature,
            ))
        items_to_add.append(GameFeature(
            appid=appid,
            feature_enumeration_id=feature_id,
        ))


    details[appid].update(game)
    SESSION.add(Game(**details[appid]))
    SESSION.commit()
    SESSION.add_all(items_to_add)
    try:
        SESSION.commit()
    except Exception as e:
        print(e)
        import ipdb; ipdb.set_trace()
(
    SESSION.query(Company)
    .filter(Company.company_id in developers)
    .update({"is_developer": True})
)
(
    SESSION.query(Company)
    .filter(Company.company_id in publishers)
    .update({"is_publisher": True})
)
SESSION.commit()
del details, publishers, developers, applist, gamedetails, feature_map, tag_map, company_map


# newsitems needs to be flattened
# date needs to be converted from unix epoch timestamp to date
# the tags need to be pulled into a separate table
tag_map = {}
author_map = {}
feedlabel_map = {}
feedname_map = {}
# accidentally created some duplicate entries
seen_gids = set()
print("parsing newsitems")
for newslist in tqdm(newsitems):
    for row in newslist:
        appid = row["appid"]
        gid = row["gid"] = int(row["gid"])
        if appid not in final_ids or gid in seen_gids:
            continue
        seen_gids.add(gid)
        row["date"] = datetime.fromtimestamp(row["date"])
        tags = row.pop("tags", [])
        newsitem_tags = []
        for tag in tags:
            tag = tag.strip()
            if tag in tag_map:
                tag_id = tag_map[tag]
            else:
                tag_id = len(tag_map) + 1
                tag_map[tag] = tag_id
                SESSION.add(NewsitemTagEnumeration(
                    newsitem_tag_enumeration_id=tag_id,
                    tag=tag,
                ))
            newsitem_tags.append(NewsitemTags(
                gid=gid,
                newsitem_tag_enumeration_id=tag_id,
            ))
        author = row.pop("author", "").strip() or None
        if author in author_map:
            author_id = author_map[author]
        elif author is None:
            author_id = None
        else:
            author_id = len(author_map) + 1
            author_map[author] = author_id
            SESSION.add(Author(
                author_id=author_id,
                author=author,
            ))
        feedlabel = row.pop("feedlabel", "").strip() or None
        if feedlabel in feedlabel_map:
            feedlabel_id = feedlabel_map[feedlabel]
        elif feedlabel is None:
            feedlabel_id = None
        else:
            feedlabel_id = len(feedlabel_map) + 1
            feedlabel_map[feedlabel] = feedlabel_id
            SESSION.add(Feedlabel(
                feedlabel_id=feedlabel_id,
                feedlabel=feedlabel,
            ))
        feedname = row.pop("feedname", "").strip() or None
        if feedname in feedname_map:
            feedname_id = feedname_map[feedname]
        elif feedname is None:
            feedname_id = None
        else:
            feedname_id = len(feedname_map) + 1
            feedname_map[feedname] = feedname_id
            SESSION.add(Feedname(
                feedname_id=feedname_id,
                feedname=feedname,
            ))
        SESSION.commit()
        SESSION.add(Newsitem(**row))
        SESSION.commit()
        SESSION.add_all(newsitem_tags)
        SESSION.commit()

SESSION.close()
