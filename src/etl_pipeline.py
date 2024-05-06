from src.service.dao.extracted_search_dao import ExtractedSearchResultDAO
from src.service.dao.raw_search_dao import RawSearchResultDAO
from src.service.extractors.search_result_extractor_abc import SearchResultExtractor


class ETLPipeline:
    def __init__(
        self,
        raw_search_result_dao: RawSearchResultDAO,
        result_extractor: SearchResultExtractor,
        extracted_search_result_dao: ExtractedSearchResultDAO,
    ) -> None:
        self._raw_search_result_dao: RawSearchResultDAO = raw_search_result_dao
        self._result_extractor: SearchResultExtractor = result_extractor
        self._extracted_search_result_dao: ExtractedSearchResultDAO = (
            extracted_search_result_dao
        )

    def run(self) -> None:
        """
        Runs the ETL pipeline

        Stage 1: Fetch raw yahoo search results
        - Queries for rows from yahoo_search_engine.search_results table after a specific date range

        Stage 2: Extract results from yahoo search results (HTML)

        Stage 3: Batch insert into PSQL (yahoo_search_results.extracted_search_results)
        - We do a CSV copy if we have millions of rows; the CSV copy would be way faster than bulk inserts
        - But in this case, since we have very few users at the moment, with very few records
        - A bulk insert is sufficient
        """
        pass


if __name__ == "__main__":
    pass
