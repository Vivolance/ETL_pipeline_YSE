import asyncio
from datetime import datetime

from src.models.extracted_search_results import ExtractedSearchResult
from src.models.last_extracted_user_status import LastExtractedUserStatus
from src.models.search_results import SearchResults
from src.models.user import User
from src.service.dao.extracted_search_dao import ExtractedSearchResultDAO
from src.service.dao.last_extracted_user_status_dao import LastExtractedUserStatusDAO
from src.service.dao.raw_search_dao import RawSearchResultDAO
from src.service.dao.user_dao import UserDAO
from src.service.extractors.bs4_extractor import BS4SearchResultExtractor
from src.service.extractors.search_result_extractor_abc import SearchResultExtractor


class ETLPipeline:
    def __init__(
        self,
        raw_search_result_dao: RawSearchResultDAO,
        last_extracted_user_dao: LastExtractedUserStatusDAO,
        user_dao: UserDAO,
        result_extractor: SearchResultExtractor,
        extracted_search_result_dao: ExtractedSearchResultDAO,
    ) -> None:
        self._raw_search_result_dao: RawSearchResultDAO = raw_search_result_dao
        self._last_extracted_user_dao: LastExtractedUserStatusDAO = (
            last_extracted_user_dao
        )
        self._user_dao: UserDAO = user_dao
        self._result_extractor: SearchResultExtractor = result_extractor
        self._extracted_search_result_dao: ExtractedSearchResultDAO = (
            extracted_search_result_dao
        )

    async def stage_one(self) -> tuple[list[SearchResults], list[User]]:
        all_users: list[User] = await self._user_dao.fetch_all_users()
        all_raw_searches_since_last_run: list[SearchResults] = []
        for user in all_users:
            last_run_status: LastExtractedUserStatus | None = (
                await self._last_extracted_user_dao.fetch_latest_status(user.user_id)
            )
            last_run: datetime = (
                last_run_status.last_run if last_run_status else datetime(1970, 1, 1)
            )
            user_str: str = user.user_id
            raw_searches_since_last_run: list[SearchResults] = (
                await self._raw_search_result_dao.fetch_searches_for_user(
                    user_str, last_run
                )
            )
            all_raw_searches_since_last_run.extend(raw_searches_since_last_run)
        return all_raw_searches_since_last_run, all_users

    async def stage_two(
        self, pre_transformed_results: list[SearchResults]
    ) -> list[ExtractedSearchResult]:
        """
        1) Loop through each list[SearchResults] and check if it is empty. Specifically the result: str attribute.
        2) if pre_transformed_results.result is None:
                continue
            else:
            run the extractor
        3) Running bs4_extractor:
            transformed_results: list[ExtractedSearchResults] = BS4SearchResultExtractor.extract(pre_transformed_results.result, pre_transformed_results.user_id)

        """
        all_transformed_results: list[ExtractedSearchResult] = []
        for pre_transformed_result in pre_transformed_results:
            if pre_transformed_result.result is None:
                continue
            else:
                transformed_results: list[ExtractedSearchResult] = (
                    self._result_extractor.extract(
                        pre_transformed_result.result, pre_transformed_result.user_id
                    )
                )
                all_transformed_results.extend(transformed_results)
        return all_transformed_results

    async def stage_three(
        self, transformed_results: list[ExtractedSearchResult], all_users: list[User]
    ) -> None:
        """
        1) Postgres recommended bulk insert record is 10,000. Batch the transformed_results into batches of 10,000
        2) Update last_extracted_user_status
            - Create a last_extracted_user_status: LastExtractedUserStatus = self._last_extracted_user_dao.create_user_status(all_users)
            - Convert all_users: list[User into list[LastExtractedUserStatus]
            - Bulk insert list[ExtractedUserStatus] in batches of 10,000 into last_extracted_user_status table
        """
        batch_size: int = 10000
        for i in range(0, len(transformed_results), batch_size):
            current_batch: list[ExtractedSearchResult] = transformed_results[
                i : i + batch_size
            ]
            await self._extracted_search_result_dao.bulk_insert(current_batch)

        all_user_status: list[LastExtractedUserStatus] = [
            LastExtractedUserStatus.create_user_status(user.user_id)
            for user in all_users
        ]

        for i in range(0, len(all_user_status), batch_size):
            current_user_batch: list[LastExtractedUserStatus] = all_user_status[
                i : i + batch_size
            ]
            await self._last_extracted_user_dao.bulk_insert_status(current_user_batch)

    async def run(self) -> None:
        """
        Runs the ETL pipeline

        Stage 1: Fetch raw yahoo search results
        - Queries for rows from yahoo_search_engine.search_results table after a specific date rang

            1) Call user_dao.fetch_all_users to fetch all users
            2) Call last_extracted_user_dao.fetch_latest_status to fetch the last run
            3) Call raw_search_dao.fetch_searches_for_user to fetch the raw results from search_results
            table since last_run

        Stage 2: Transform results obtained from stage 1 from yahoo search results table (HTML)
            1) Results can be none (check search_results model to see the attribute) If it is a none
            we should not transform. Hence, we should create a guard (if-else)
            2) Call result_extractor.extract(result: str, user_id: str) to transform the raw_search into
            list[ExtractedSearchResults].

        Stage 3: Batch insert into PSQL (yahoo_search_results.extracted_search_results)
        - We do a CSV copy if we have millions of rows; the CSV copy would be way faster than bulk inserts
        - But in this case, since we have very few users at the moment, with very few records
        - A bulk insert is sufficient
            1) Call extracted_search_dao.bulk_insert(list[ExtractedResults) to bulk insert into
            extracted_search_results table
            2) Update the last_extracted_user_status
        """
        raw_results: list[SearchResults]
        users: list[User]
        raw_results, users = await self.stage_one()
        transformed_results: list[ExtractedSearchResult] = await self.stage_two(
            raw_results
        )
        await self.stage_three(transformed_results, users)


if __name__ == "__main__":
    raw_search_dao: RawSearchResultDAO = RawSearchResultDAO()
    last_extracted_user_dao: LastExtractedUserStatusDAO = LastExtractedUserStatusDAO()
    user_dao: UserDAO = UserDAO()
    result_extractor: BS4SearchResultExtractor = BS4SearchResultExtractor()
    extracted_search_result_dao: ExtractedSearchResultDAO = ExtractedSearchResultDAO()

    etl_pipeline: ETLPipeline = ETLPipeline(
        raw_search_dao,
        last_extracted_user_dao,
        user_dao,
        result_extractor,
        extracted_search_result_dao,
    )
    event_loop = asyncio.new_event_loop()
    event_loop.run_until_complete(etl_pipeline.run())
