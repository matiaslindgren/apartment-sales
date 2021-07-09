import argparse
import sqlite3

import requests
import pandas as pd
from pyjstat import pyjstat

import queries

used_years = [
    2013,
    2014,
    2015,
    2016,
    2017,
    2018,
    2019,
]


def fetch_dataframe(url, query):
    """
    Post a JSON query to a pxnet2.stat.fi API endpoint.
    Parse the response into a pandas.DataFrame.
    """
    r = requests.post(url, json=query)
    r.raise_for_status()
    df = pyjstat.from_json_stat(r.json())
    return df[0]


def simplify_postal_codes(df):
    # Split postal codes by space and select first part
    df["postal_code"] = df["postal_code"].str.split(' ', 1, expand=True)[0]
    # Drop rows where the postcode is not a string of 5 digits
    df = df[df["postal_code"].str.contains("\d{5}")]
    return df


def cleanup_dwellings_data(df):
    df = df.rename(
        columns={
            "Postal code area": "postal_code",
            "value": "dwellings",
            "Data": "Information",
        })
    del df["Information"]
    df = simplify_postal_codes(df)
    # If any column of a row contains a NaN, drop the row
    df = df.dropna()
    return df


def cleanup_sales_data(df):
    df = df.rename(columns={
        "Year": "year",
        "Postal code": "postal_code",
        "value": "sales"
    })
    unused_columns = [
        "Building type",
        "Year of construction",
        "Information",
    ]
    for col in unused_columns:
        del df[col]
    df = simplify_postal_codes(df)
    df["year"] = df["year"].astype(int)
    df = df.dropna()
    return df


def fetch_sales_by_years(years):
    url, query = queries.generate_sales_query(years)
    df = fetch_dataframe(url, query)
    df = cleanup_sales_data(df)
    return df


def fetch_dwellings_by_year(year):
    url, query = queries.generate_paavo_query(year)
    df = fetch_dataframe(url, query)
    df = cleanup_dwellings_data(df)
    df["year"] = int(year)
    # Select postal code areas with at least 1 apartment
    df = df[df["dwellings"] > 0]
    return df


def fetch_all():
    # Use a single query to fetch sales data for all years
    sales = fetch_sales_by_years(used_years)
    # Use multiple fetches to concatenate Paavo data for each year
    dwellings = pd.concat(
        [fetch_dwellings_by_year(year) for year in used_years],
        ignore_index=True)
    return sales, dwellings


def compute_turnover(sales, dwellings):
    result = pd.merge(sales, dwellings, on=["postal_code", "year"])
    result["turnover"] = result["sales"] / result["dwellings"]
    assert result.notna().all().all(), "NaNs in data after computing turnover"
    return result


def main(db_path):
    sales, dwellings = fetch_all()
    df = compute_turnover(sales, dwellings)
    with sqlite3.connect(db_path) as db_conn:
        df.to_sql("apartment_sales", db_conn)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "db_path",
        type=str,
        help="Path for generated sqlite3 database. It should not exist.")
    args = parser.parse_args()

    main(args.db_path)
