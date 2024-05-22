from datetime import datetime

import pytest

from integration_tests.conftest import integration_test_db_config
from integration_tests.src.utils.clear_tables import ClearTables
from integration_tests.src.utils.engine import dummy_uuid
from integration_tests.src.utils.fetch import Fetch
from integration_tests.src.utils.insert import Insert
from src.models.extracted_search_results import ExtractedSearchResult
from src.models.user import User
from src.service.dao.extracted_search_dao import ExtractedSearchResultDAO


"""
Steps to create integration test_etl_pipeline.py for insert_search method
Pre: Create a new database used for integration testing
1) Prepare the state for testing by cleaning up the table in the db
2) Act -> Executing the main function to run the code
3) Assert -> Asserts that the insert works by reading from the table
4) Clean up
"""

"""
The constructor is to cache attributes that are used throughout the object

Im missing insert_user IT. 
Plan: Create a fetch_user method in the integration test_etl_pipeline.py folder. Clear user table
Act: Call the extracted_search_dao.insert_user method to insert dummy users into the user table
Asset: Use self.fetch_all_users to fetch the inserted rows and assert it
Clear user tables
"""


EXTRACTED_SEARCH_DAO: ExtractedSearchResultDAO = ExtractedSearchResultDAO(
    integration_test_db_config()
)


class TestExtractedSearchResultDAO:

    @pytest.mark.asyncio_cooperative
    async def test_insert_users(self) -> None:
        await ClearTables.clear_users_table()
        users: list[User] = [
            User(
                user_id=str(dummy_uuid),
                created_at=datetime(year=2024, month=5, day=17, hour=17),
            )  # 0x123
        ]
        for user in users:
            await EXTRACTED_SEARCH_DAO.insert_user(user)
        results: list[User] = await Fetch.fetch_users()
        assert results == users
        await ClearTables.clear_users_table()

    @pytest.mark.asyncio_cooperative
    async def test_insert_search(self) -> None:
        await ClearTables.clear_users_table()
        await ClearTables.clear_extracted_search_results_table()
        users: list[User] = [
            User(
                user_id=str(dummy_uuid),
                created_at=datetime(year=2024, month=5, day=14, hour=12),
            )
        ]
        for user in users:
            await Insert.insert_user(user)

        extracted_search_results: list[ExtractedSearchResult] = [
            ExtractedSearchResult(
                id="dummy id",
                user_id=str(dummy_uuid),
                url="dummy url",
                date="2024-05-30",
                body="dummy results",
                created_at=datetime(year=2024, month=5, day=14, hour=13),
            )
        ]

        for extracted_search_result in extracted_search_results:
            await EXTRACTED_SEARCH_DAO.insert_search(extracted_search_result)

        results_row: list[ExtractedSearchResult] = (
            await Fetch.fetch_all_searches_from_extracted_search_results()
        )
        assert results_row == extracted_search_results
        await ClearTables.clear_extracted_search_results_table()
        await ClearTables.clear_users_table()

    @pytest.mark.asyncio_cooperative
    async def test_bulk_insert(self) -> None:
        """
        Test Plan:
        1) Prepare the table for IT (done by alembic, clear table)
        2) Act (execute the bulk_insert function call to insert rows into the table
        3) Assert that each row in the table is inserted correctly
        4) Clear the table
        """
        await ClearTables.clear_users_table()
        await ClearTables.clear_extracted_search_results_table()
        users: list[User] = [
            User(
                user_id=str(dummy_uuid),
                created_at=datetime(year=2024, month=5, day=15, hour=14),
            )
        ]

        for user in users:
            await Insert.insert_user(user)

        extracted_search_results: list[ExtractedSearchResult] = [
            ExtractedSearchResult(
                id="dummy id",
                user_id=str(dummy_uuid),
                url="dummy url",
                date="2024-05-30",
                body="dummy result",
                created_at=datetime(year=2024, month=5, day=14, hour=13),
            )
        ]

        for extracted_search_result in extracted_search_results:
            await EXTRACTED_SEARCH_DAO.insert_search(extracted_search_result)

        results_row: list[ExtractedSearchResult] = (
            await Fetch.fetch_all_searches_from_extracted_search_results()
        )
        assert results_row == extracted_search_results
        await ClearTables.clear_extracted_search_results_table()
        await ClearTables.clear_users_table()

    @pytest.mark.asyncio_cooperative
    async def test_fetch_all_searches(self) -> None:
        await ClearTables.clear_users_table()
        await ClearTables.clear_extracted_search_results_table()
        users: list[User] = [
            User(
                user_id=str(dummy_uuid),
                created_at=datetime(year=2024, month=5, day=15, hour=15),
            )
        ]
        for user in users:
            await Insert.insert_user(user)

        extracted_search_results: list[ExtractedSearchResult] = [
            ExtractedSearchResult(
                id="dummy id",
                user_id=str(dummy_uuid),
                url="dummy url",
                date="2024-05-15",
                body="dummy results",
                created_at=datetime(year=2024, month=5, day=15, hour=16),
            )
        ]

        for extracted_search_result in extracted_search_results:
            await Insert.insert_search_extracted_search_results(extracted_search_result)

        results_row: list[ExtractedSearchResult] = (
            await EXTRACTED_SEARCH_DAO.fetch_all_searches()
        )
        assert results_row == extracted_search_results
        await ClearTables.clear_extracted_search_results_table()
        await ClearTables.clear_users_table()
