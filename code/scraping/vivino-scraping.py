# Import packages
from ast import Break
from bdb import Breakpoint
import requests
import json
import pandas as pd

# Get request from the Vivino website


def get_wine_data(wine_id, year, page):
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:89.0) Gecko/20100101 Firefox/89.0",
    }

    api_url = f"https://www.vivino.com/api/wines/{wine_id}/reviews?per_page=50&year={year}&page={page}"
    print(api_url)

    data = requests.get(api_url, headers=headers).json()

    return data

all_reviews = pd.DataFrame(columns=["Year", "Wine ID", "Wine Name", "Country",
                          "Structure", "Style", "User Rating", "Note", "CreatedAt", "Wine Type"])

for i in range(100,120):
    print('AAAAAAAAAAAAAAAAAAAA ' + str(i) + '\n\n\n\n\n')
    # Get request from the Vivino website
    r = requests.get(
        "https://www.vivino.com/api/explore/explore",
        params={
            # "country_codes[]": ["pt", "es", "fr"],  # <-- put more country codes here
            "currency_code": "EUR",
            "grape_filter": "varietal",
            "min_rating": "1",
            "order_by": "price",
            "order": "asc",
            "page": i,
            "price_range_max": "500",
            "price_range_min": "0",
            "wine_type_ids[]": "1",
        },
        headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:66.0) Gecko/20100101 Firefox/66.0"
        },
    )


    def style(t):
        # print(t["vintage"]["wine"])
        try:
            return t["vintage"]["wine"]["style"]["name"]
        except:
            return None


    def w_type(t):
        try:
            return t["vintage"]["wine"]["style"]["wine_type_id"]
        except:
            return None


    # Variables to scrape from the Vivino website
    results = [
        (
            t["vintage"]["wine"]["winery"]["name"],
            t["vintage"]["year"],
            t["vintage"]["wine"]["id"],
            t["vintage"]["wine"]["name"],
            t["vintage"]["wine"]["region"]["country"]["name"],
            t["vintage"]["wine"]["taste"]["structure"],
            style(t),
            w_type(t)
            # f'{t["vintage"]["wine"]["name"]} {t["vintage"]["year"]}',
        )
        for t in r.json()["explore_vintage"]["matches"]
    ]

    # print(json.dumps(r.json()['explore_vintage']['matches'][0]
    #      ['vintage']['wine']['style'], indent=4))
    # Saving the results in a dataframe
    dataframe = pd.DataFrame(
        results,
        columns=["Winery", "Year", "Wine ID", "Name", "Country", "Structure", "Style", "Wine Type"],
    )

    # Scraping the reviews from the Vivino website
    ratings = []

    for _, row in dataframe.iterrows():

        page = 1
        i = 0
        while True:
            print(
                f'Getting info about wine {row["Wine ID"]}-{row["Year"]} Page {page}'
            )

            d = get_wine_data(row["Wine ID"], row["Year"], page)

            if not d["reviews"]:
                break

            if i == 0:
                print(row)
                i = 1

            for r in d["reviews"]:
                if r["language"] != "en":  # <-- get only english reviews
                    continue
                ratings.append(
                    [
                        row["Year"],
                        row["Wine ID"],
                        row["Name"],
                        row["Country"],
                        str(row["Structure"]),
                        row["Style"],
                        r["rating"],
                        r["note"],
                        r["created_at"],
                        row["Wine Type"]
                    ]
                )
            page += 1

            if page == 5:
                break
        else:
            break


    ratings = pd.DataFrame(
        ratings, columns=["Year", "Wine ID", "Wine Name", "Country",
                          "Structure", "Style", "User Rating", "Note", "CreatedAt", "Wine Type"]
    )
    all_reviews = all_reviews.append(ratings)
# Merging the two datasets; results and ratings.
# df_out = ratings.merge(dataframe, on=['Year', 'Wine ID', 'Wine N'])
# df_out.to_csv("data.csv", index=False)
all_reviews.to_csv("data100_120.csv", index=False)
