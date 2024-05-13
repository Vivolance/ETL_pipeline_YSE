from bs4 import BeautifulSoup

"""
NOT IN USE, USED AS PROTOTYPES
"""

def bs4_extract_text(input_html: str) -> str:
    """
    Extracts text from HTML

    Approach 1: BS4 with standard html.parser

    BS4 seems to be bad at the following
    - It doesn't preserve what is a search result and what is not; Not clear
    - Some content we want might have been erased
    """
    soup: BeautifulSoup = BeautifulSoup(input_html, "html.parser")
    text: str = soup.get_text()
    return text


def bs4_is_html(body: str) -> bool:
    """
    Checks if a body is a HTML or not

    Observation: Wonky
    """
    return bool(BeautifulSoup(body, "html.parser").find())
