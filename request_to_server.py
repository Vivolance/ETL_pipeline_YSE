import logging
from pydoc import Doc
import requests
from typing import Any
import spacy
from spacy import Language
from spacy.matcher import Matcher

from utils.file_cache import file_cache
from bs4 import BeautifulSoup
import html2text
from lxml import html


LOGGER: logging.Logger = logging.Logger(__name__)

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

def html2text_extract_text(input_html: str) -> str:
    """
    Approach 2: Use html2text

    Extracts text from HTML, but preserves the structure of the html document as well
    - Result is unsatisfactory
    """
    h = html2text.HTML2Text()
    h.ignore_links = True
    text = h.handle(input_html)
    return text


def extract_text_preserving_structure(html_content: str) -> str:
    """
    Approach 3: Use BS4 with recursion
    """
    soup = BeautifulSoup(html_content, 'html.parser')
    # This function will recursively walk through the soup tree
    def recurse_through_soup(soup_element):
        texts = []
        for element in soup_element.children:
            if isinstance(element, str):  # If the element is a NavigableString, capture it
                text = element.strip()
                if text:  # Avoid capturing empty or whitespace-only strings
                    texts.append(text)
            elif element.name in ['p', 'div', 'li']:  # You can add more tags as needed
                # Recursively process each element and join its texts with a newline
                sub_texts = recurse_through_soup(element)
                if sub_texts:
                    texts.append('\n'.join(sub_texts))
            else:
                # Recursively process other elements without adding newlines
                sub_texts = recurse_through_soup(element)
                if sub_texts:
                    texts.extend(sub_texts)
        return texts

    extracted_texts = recurse_through_soup(soup)
    # Join all segments with double newlines to preserve separation
    final_text = '\n\n'.join(extracted_texts)
    return final_text


def detect_html_patterns(doc: Doc):
    matcher = Matcher(nlp.vocab)
    # Define pattern for typical HTML tags
    pattern = [{'ORTH': '<'}, {'IS_ALPHA': True, 'OP': '+'}, {'ORTH': '>'}]
    matcher.add('HTML_TAG', [pattern])
    matches = matcher(doc)
    for match_id, start, end in matches:
        span = doc[start:end]  # The matched span
        print("Found HTML tag:", span.text)


if __name__ == "__main__":
    """
    Steps to implement a machine learning feature, or any feature for that matter
    
    Step 1: Take the project and cut it down into multiple parts
    Step 2: Isolate the most difficult part of the project
    - The most difficult part here, is cleaning the HTML on behalf of the user
    Step 3: Come up with possible approaches for the implementation
    
    Approach 1: Use a HTML Parser, no ML. Brute force the HTMl and come up with a hard-coded HTMl parser
    - This is not great; it breaks once yahoo or google changes it's HTML layout
    
    Approach 2: Use a bazooka to kill the ant. Send the whole payload into ChatGPT3.5 and make it extract it
    - This is still not great; ChatGPT3.5 API costs a sub-cent per call
    
    Approach 3: Using Classical Machine Learning / Simpler Deep Learning
    - We transform the data into features ourselves, the same features ChatGPT would have learnt by itself
    - No choice, as using a more stupid model means we have to make the task easy for it right?
    
    Features:
    - text -> tokens (tokens are like sub-words, elephant -> ele phant, 2 tokens)
    - convert tokens into vectors; these vectors represent the meaning behind the word
    
    spacy has 3 models
    - en-core-web-sm -> smallest model, Convolutional neural network small
        - small model is light in RAM usage, and very fast
    - en-core-web-lg -> larger model, Convolutional neural network
        - recommended default, and it's a good balance between speed and quality
    - en-core-web-trf -> one of the larger models, Transformer
        - performs better than en-core-web-lg, but slower
    """
    results: dict[str, Any] = get_search_results("coffee")
    nlp: Language = spacy.load("en_core_web_lg")
    yahoo_html: str = results["result"]
    """
    Step 1: Convert HTML into Text + HTML
    """
    raw_text: str = bs4_extract_text(extract_text_preserving_structure(yahoo_html))
    # print(raw_text)

    """
    Step 2: Tag text as search result or not
    - For parts which are search results, we keep them
    - For non search results, we erase them
    """
    doc: Doc = nlp(raw_text)
    # for token in doc:
    #    print(token.text, token.ent_type_, token.ent_iob_)
    print(doc)
    # doc = nlp(raw_text)
    # detect_html_patterns(doc)
    # print(type(doc))

