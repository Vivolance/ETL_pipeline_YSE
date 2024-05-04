from typing import Any

import requests

from utils.file_cache import file_cache


@file_cache
def get_search_results(query: str) -> dict[str, Any]:
    """
    Makes a request to yahoo search engine, and gets back the body.
    """
    url: str = "http://localhost:8080/search"
    body: dict[str, Any] = {
        "user_id": "2843e37d-543c-4b76-8ef3-ed78e09cd57d",
        "query": query
    }
    results: requests.Response = requests.post(url, json=body)
    print(f"status_code: {results.status_code}")
    return results.json()
