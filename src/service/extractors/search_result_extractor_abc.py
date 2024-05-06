from abc import ABC, abstractmethod

from src.models.extracted_search_results import ExtractedSearchResult


class SearchResultExtractor(ABC):
    @abstractmethod
    def extract(self, html: str) -> list[ExtractedSearchResult]:
        raise NotImplementedError("Not Implemented")
