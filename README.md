This repo leverages data available via the [Steamworks API](https://partner.steamgames.com/doc/api) and data scraped from the [Steam](https://store.steampowered.com) webpage.

Code in this repo is executed using `Python 3.9.5`. Pinned python packages can be found in [requirements.txt](requirements.txt).

The scripts in this repo were written in the following order and accomplish the following:
1. [explore_api.py](src/explore_api.py) - figure out what data is readily available via the Steamworks API and create a plan for retrieving that data.
2. [get_raw_data.py](src/get_raw_data.py) - aggregate the data from the Steamworks API into json files for later use.
3. [scrape_game_pages.py](src/scrape_game_pages.py) - based on the list of games for which Steamworks API data was available, crawl the Steam webpage to gather additional data for each game. Save those results in a json file for later use.
4. [create_dataframes.py](src/create_dataframes.py) - organize the collected data into Pandas DataFrames and save them into csv files for later use.
