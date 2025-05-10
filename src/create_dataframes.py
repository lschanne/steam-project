import json
import os
import pandas as pd

from constants import DATA_DIR

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

# newsitems needs to be flattened
# the tags need to be pulled into a separate table
newsitems_data = []
newsitem_tags = []
for newslist in newsitems:
    for row in newslist:
        appid = row["appid"]
        if appid in final_ids:
            tags = row.pop("tags", [])
            newsitems_data.append(row)
            newsitem_tags.extend([{"gid": row["gid"], "tag": tag} for tag in tags])
newsitems_df = pd.DataFrame(newsitems_data)
newsitems_df.to_csv(os.path.join(DATA_DIR, "newsitems.csv"))
newsitem_tags_df = pd.DataFrame(newsitems_data)
newsitem_tags_df.to_csv(os.path.join(DATA_DIR, "newsitem_tags.csv"))
del newsitems_data, newsitem_tags, newsitems_df, newsitem_tags_df, newsitems

# add the name from applist to gamedetails
details = {}
for app in applist:
    appid = app["appid"]
    if appid in final_ids:
        details[appid] = app

# developers, publishers, tags, and features should be pulled out of gamedetails into separate dataframes
developers = []
publishers = []
tags = []
features = []
for game in gamedetails:
    appid = game["appid"]
    if not appid in final_ids:
        continue
    developers.extend([
        {"appid": appid, "developer": x} for x in game.pop("developers", [])
    ])
    publishers.extend([
        {"appid": appid, "publisher": x} for x in game.pop("publishers", [])
    ])
    # the steam page for games has a "+" button to add tags; I should have filtered it out in
    # the web scraping, but I will do it here since I missed it before
    tags.extend([
        {"appid": appid, "tag": x} for x in game.pop("tags", []) if x != "+"
    ])
    features.extend([
        {"appid": appid, "feature": x} for x in game.pop("features", [])
    ])
    details[appid].update(game)
details_df = pd.DataFrame(details.values())
details_df.to_csv(os.path.join(DATA_DIR, "details.csv"))
developers_df = pd.DataFrame(developers)
developers_df.to_csv(os.path.join(DATA_DIR, "developers.csv"))
publishers_df = pd.DataFrame(publishers)
publishers_df.to_csv(os.path.join(DATA_DIR, "publishers.csv"))
tags_df = pd.DataFrame(tags)
tags_df.to_csv(os.path.join(DATA_DIR, "tags.csv"))
features_df = pd.DataFrame(features)
features_df.to_csv(os.path.join(DATA_DIR, "features.csv"))

