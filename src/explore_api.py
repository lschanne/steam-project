"""
https://partner.steamgames.com/doc/webapi_overview
https://partner.steamgames.com/doc/api
"""

import requests

API_BASE = "https://api.steampowered.com"

# Gets the complete list of public apps.
# List[Dict[str, Union[str, int]]]
# keys:
#   appid: int
#   name: str
applist = requests.get(
    f"{API_BASE}/ISteamApps/GetAppList/v2/",
).json()["applist"]["apps"]

# need to iterate over appid
# appnews is a dict with 
#   appid: int
#   count: int
#   newsitems: Dict[List[str, Any]]
appnews = requests.get(
    f"{API_BASE}/ISteamNews/GetNewsForApp/v2/",
    params={"appid": 20},
).json()['appnews']
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

# List[Dict[str, str]]
#   name: str
#   percent: str (ex: '24.2')
achievements = requests.get(
    f"{API_BASE}/ISteamUserStats/GetGlobalAchievementPercentagesForApp/v2/",
    params={"gameid": 300},
).json()['achievementpercentages']['achievements']

"""
https://partner.steamgames.com/doc/webapi/ISteamUserStats
TODO not sure how to get valid `name[0]` values. This is supposed to be the name of the stat.
Also not sure how to determine `count`
requests.get(f"{API_BASE}/ISteamUserStats/GetGlobalStatsForGame/v1/", params={"appid": 300, "count": 20, "name[0]": 20}).json()
"""

"""
seems to transient too be useful
requests.get(f"{API_BASE}/ISteamUserStats/GetNumberOfCurrentPlayers/v1/", params={"appid": 300}).json()
ex: {'response': {'player_count': 346, 'result': 1}}
"""
