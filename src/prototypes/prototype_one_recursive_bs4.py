import logging
from typing import Any

from src.utils.get_search_results import get_search_results
from src.utils.logger_utils import setup_logger
from src.utils.recursive_bs4_extract_text_utils import (
    bs4_recursive_extract_text,
    ExtractedTextGroup,
)

LOGGER: logging.Logger = logging.Logger(__name__)
setup_logger(LOGGER)

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
    results: dict[str, Any] = get_search_results("tesla earning reports")
    print(f"Results: {results}")
    # nlp: Language = spacy.load("en_core_web_lg")
    yahoo_html: str = results["result"]
    """
    Step 1: Convert HTML into Text + HTML
    - If we pass each segment into bs4_extract_text at a time, it might be better
    - Having both text and HTML versions gives you flexibility in how you handle and manipulate 
    the data. You can work with the text version for analysis or display purposes, while still 
    having access to the original HTML for tasks like reformatting, re-parsing, or extracting 
    additional information.
    """
    raw_text: list[ExtractedTextGroup] = bs4_recursive_extract_text(yahoo_html)

    for single_result in raw_text:
        LOGGER.info("=====")
        LOGGER.info(single_result)
