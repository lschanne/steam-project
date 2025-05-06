
import json
import os
import requests
from tqdm import tqdm

from constants import DATA_DIR

API_BASE = "https://api.steampowered.com"

if not os.path.exists(DATA_DIR):
  os.makedirs(DATA_DIR)

# Gets the complete list of public apps.
# List[Dict[str, Union[str, int]]]
# keys:
#   appid: int
#   name: str
fh = os.path.join(DATA_DIR, "applist.json")
if not os.path.exists(fh):
    print("Using API to get applist")
    applist = requests.get(
        f"{API_BASE}/ISteamApps/GetAppList/v2/",
    ).json()["applist"]["apps"]
    with open(fh, "w") as f:
        f.write(json.dumps(applist))
else:
    print(f"Found {fh}")
    with open(fh, "r") as f:
        applist = json.loads(f.read())

# need to iterate over appid
# appnews is a dict with
#   appid: int
#   count: int
#   newsitems: Dict[List[str, Any]]
fh = os.path.join(DATA_DIR, "newsitems.json")
if os.path.exists(fh):
    print(f"Found {fh}")
    with open(fh, "r") as f:
        all_newsitems = json.loads(f.read())
else:
    all_newsitems = []
    max_idx = -1
    for name in os.listdir(DATA_DIR):
        if not name.startswith("appnews_"):
            continue
        with open(os.path.join(DATA_DIR, name), "r") as f:
            all_newsitems.append(json.loads(f.read()))
        idx = int(name.split("_", 1)[1].rsplit(".", 1)[0])
        max_idx = max(max_idx, idx)
    print(f"Starting from idx {max_idx}")
    for idx in tqdm(range(max_idx + 1, len(applist))):
        try:
            appid = applist[idx]["appid"]
        except Exception as e:
            continue
        appnews = requests.get(
            f"{API_BASE}/ISteamNews/GetNewsForApp/v2/",
            params={"appid": appid},
        ).json()
        if not "appnews" in appnews:
            continue
        appnews = appnews['appnews']
        # newsitems is a dict with the keys
        #   gid: str (contains an int)
        #   title: str
        #   url: str
        #   is_external_url: bool
        #   author: str
        #   contents: str
        #   feedlabel: str
        #   date: int
        #   feedname: str
        #   feed_type: int
        #   appid: int
        #   tags: List[str]
        newsitems = appnews["newsitems"]
        with open(os.path.join(DATA_DIR, f"appnews_{idx}.json"), "w") as f:
            f.write(json.dumps(newsitems))
        all_newsitems.append(newsitems)
    with open(fh, "w") as f:
        f.write(json.dumps(all_newsitems))

for name in os.listdir(DATA_DIR):
    if name.startswith("appnews_"):
        os.remove(os.path.join(DATA_DIR, name))

# List[Dict[str, str]]
#   name: str
#   percent: str (ex: '24.2')
fh = os.path.join(DATA_DIR, "achievements.json")
if os.path.exists(fh):
    print(f"Found {fh}")
    with open(fh, "r") as f:
        all_achievements = json.loads(f.read())
else:
    all_achievements = []
    max_idx = -1
    for name in os.listdir(DATA_DIR):
        if not name.startswith("achievements_"):
            continue
        with open(os.path.join(DATA_DIR, name), "r") as f:
            s = f.read()
        try:
            value = json.loads(s)
        except Exception as e:
            os.remove(os.path.join(DATA_DIR, name))
            continue
        all_achievements.append(value)
        idx = int(name.split("_", 1)[1].rsplit(".", 1)[0])
        max_idx = max(max_idx, idx)
    print(f"Starting from idx {max_idx}")
    for idx in tqdm(range(max_idx + 1, len(applist))):
        try:
            appid = applist[idx]["appid"]
        except Exception as e:
            continue
        achievements = requests.get(
            f"{API_BASE}/ISteamUserStats/GetGlobalAchievementPercentagesForApp/v2/",
            params={"gameid": appid},
        ).json()
        if not "achievementpercentages" in achievements:
            continue
        achievements = achievements['achievementpercentages']['achievements']
        with open(os.path.join(DATA_DIR, f"achievements_{idx}.json"), "w") as f:
            f.write(json.dumps(achievements))
        all_achievements.append(achievements)
    with open(os.path.join(DATA_DIR, "achievements.json"), "w") as f:
        f.write(json.dumps(all_achievements))

for name in os.listdir(DATA_DIR):
    if name.startswith("achievements_"):
        os.remove(os.path.join(DATA_DIR, name))
