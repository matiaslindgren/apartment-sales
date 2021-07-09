"""
Functions for generating correct pxnet2.stat.fi API URLs and queries for different years.
"""


def generate_paavo_query(year):
    paavo_baseurl = "https://pxnet2.stat.fi:443/PXWeb/api/v1/en/Postinumeroalueittainen_avoin_tieto"
    if year < 2018:
        api_url = paavo_baseurl + "/{0}/paavo_6_ra_{0}.px".format(year + 2)
        selection_key = "Ra_asunn"
    else:
        api_url = paavo_baseurl + "/{}/paavo_pxt_12f4.px".format(year + 2)
        selection_key = "ra_asunn"
    query = {
        "query": [
            {
                "code": "Tiedot",
                "selection": {
                    "filter": "item",
                    "values": [selection_key],
                },
            },
        ],
        "response": {
            "format": "json-stat2",
        },
    }
    return api_url, query


def generate_sales_query(years):
    api_url = "https://pxnet2.stat.fi:443/PXWeb/api/v1/en/StatFin/asu/ashi/vv/statfin_ashi_pxt_112q.px"
    query = {
        "query": [{
            "code": "Talotyyppi",
            "selection": {
                "filter": "item",
                "values": ["6"]
            }
        }, {
            "code": "Rakennusvuosi",
            "selection": {
                "filter": "item",
                "values": ["0"]
            }
        }, {
            "code": "Vuosi",
            "selection": {
                "filter": "item",
                "values": years,
            }
        }, {
            "code": "Tiedot",
            "selection": {
                "filter": "item",
                "values": ["lkm_julk"]
            }
        }],
        "response": {
            "format": "json-stat2"
        }
    }
    return api_url, query
