import requests
import pandas as pd

from .utils.extra import random_user_agent
from .utils.screen_obj import ScreenerParams
from .utils.screen_result_obj import ScreenResultObj


def screener(params, n_results=500, as_dataframe=True):
    """


    Args:
        params (:obj:`ScreenerParams`): Screening parameters
        n_results (:obj:int): The maximum number of results to return

    Returns:
        :obj:`list` of :obj:`investpy.utils.search_obj.SearchResultObj`: if as_dataframe is false
        :obj:`pandas.DataFrame: if as_dataframe is true
        The financial data of all securities that match the criteria in `params`. If no matches are
        foundm the resulting list or dataframe will be empty


    Raises:
        ValueError: raised whenever any of the introduced parameter is not valid or errored.
        ConnectionError: raised whenever the connection to Investing.com failed.
        RuntimeError: raised when there was an error while executing the function.

    """

    if not (params and isinstance(params, ScreenerParams)):
        raise ValueError('ERR#0074: params parameter is mandatory and it must be a ScreenerParams instance.')

    params = params.finish()

    head = {
        "User-Agent": random_user_agent(),
        "X-Requested-With": "XMLHttpRequest",
        "Accept": "text/html",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive",
    }

    url = 'https://www.investing.com/stock-screener/Service/SearchStocks'

    n_fetched = 0
    pn = 1
    search_results = []

    while n_fetched < n_results:
        params["pn"] = pn
        req = requests.post(url, headers=head, data=params)
        if req.status_code != 200:
            raise ConnectionError("ERR#0015: error " + str(req.status_code) + ", try again later.")

        data = req.json()

        if data['totalCount'] < n_results:
            n_results = data['totalCount']

        n_fetched += len(data["hits"])
        pn += 1

        search_results += [ScreenResultObj(rec) for rec in data["hits"]]

    return to_dataframe(search_results) if as_dataframe else search_results

def to_dataframe(results):
    df = pd.DataFrame(data=[rec.as_dict() for rec in results])
    df.set_index("id")
    return df