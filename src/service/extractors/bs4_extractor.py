from src.models.extracted_text_group import ExtractedTextGroup
from src.models.extracted_search_results import ExtractedSearchResult
from src.service.extractors.search_result_extractor_abc import SearchResultExtractor
from src.utils.recursive_bs4_extract_text_utils import bs4_recursive_extract_text


class BS4SearchResultExtractor(SearchResultExtractor):
    """
    Approach 1: BS4 HTML traversal (Non-ML)
    Use BS4 to traverse HTML as a tree
    - Recursively traverse the HTML, saving the parent tags of each HTML component

    Assume Search Results from Yahoo always appears in a <ul> or <ol>
    - Each component within the same <li> are a single search result
    - Search results have at least a body + date; filter out those that don't
    """

    def __init__(self) -> None:
        return

    def extract(self, html: str) -> list[ExtractedSearchResult]:
        unfiltered_group: list[ExtractedTextGroup] = bs4_recursive_extract_text(html)
        filtered_group: list[ExtractedTextGroup] = [
            group for group in unfiltered_group if group.information_count >= 2
        ]
        extracted_search_results: list[ExtractedSearchResult] = [
            ExtractedSearchResult.from_extracted_text_group(group)
            for group in filtered_group
        ]
        return extracted_search_results
